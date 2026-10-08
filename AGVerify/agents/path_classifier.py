#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""path_classifier: 通路族语义归类 agent(供 path_guidance 调用)

输入: gate 决策 + 全量截断通路清单 + 公式信号映射
输出: {families: [{name, obligation, note, members: [通路原文]}]}
      members 并集 = 输入通路全集(每条归且仅归一族)
结果由 path_guidance 缓存(内存+磁盘), 同一 (module, formula) 只调一次。
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from llm import chat  # noqa: E402

EMBEDDED_PROMPT = """你是硬件协议分析专家。输入是 SoC 通道依赖图的义务定位与
通路清单(已截断保留最短主干):
- signal_map 给出公式中每个别名对应的实际信号(module + 端口路径)
- verdict 说明每个因果对的义务归属: local(本模块)/trivial(自然满足)/
  transfer(转移他模块)/global(需环境组合)/env(真环境)/cycles(回馈环)
- 每条通路是通道节点序列: <实例>.<通道>.[fwd|bwd] (代表端口路径[模块]),
  fwd=请求/数据正向, bwd=ready 反压; 已按长度升序
- riscv-mini: icache/dcache(带miss状态机的Cache) 共享 nasti 总线, arb 仲裁,
  dpath 五级流水

任务: 自己对全部通路做聚类和解释——按语义原型分组(同骨架仅 nasti
出口/次序不同 → 同一族), 结果供 decomposer 直接消费。

输出 JSON:
{
 "families": [{"name": "语义名(如 写回+二次访存)",
               "obligation": "环境|设计|混合",
               "note": "该族的语义解释: 反映什么协议行为/义务归属/可疑伪环",
               "members": [属于该族的输入通路【序号】列表, 如 [1, 5, 9]]}]
}
规则: 每条输入通路必须归入且只归入一个族——所有 members 序号并集 =
输入全集且互不重叠; 族数控制在 3-6 个。"""


def paths_text(brief: dict) -> str:
    """brief → 可读通路清单(与 LLM 输入一致, 供草稿存档)"""
    text = []
    idx = 0
    for it in brief.get('items', []):
        if 'pair' in it:
            text.append('### 信号对 {} → {} ({})'.format(
                *it['pair'], it.get('why', '')))
            text.append('共 {} 条通路(静态轨迹聚类 {} 族), 每条前缀为序号:'.format(
                it.get('path_count'), it.get('trace_family_count')))
            for p in it.get('paths', []):
                idx += 1
                text.append('{} {}'.format(idx, p))
        else:
            text.append('### 单信号 {} (回馈环)'.format(it.get('signal')))
            for c in it.get('cycles', []):
                idx += 1
                text.append('{} {}'.format(idx, c))
        text.append('')
    return '\n'.join(text)


def classify(module: str, formula: str, gate: dict, brief: dict,
             signal_map: dict = None) -> dict:
    """一次 LLM 归类调用(输入为全量截断通路清单)。失败抛异常(调用方降级)。"""
    payload = {
        'module': module,
        'formula': formula,
        'signal_map': signal_map or {},     # 公式别名 → {module, port}
        'gate_verdicts': [
            {'pair': p['pair'], 'verdict': p['verdict'],
             'why': p['why']} for p in gate.get('pairs', [])],
        '__text__': {'通路清单': paths_text(brief)},
    }
    r = chat('path_classifier', EMBEDDED_PROMPT, payload, json_mode=True)
    parsed = r.get('parsed')
    if parsed is None:
        raise ValueError('path_classifier 输出非 JSON: {}'
                         .format(str(r.get('content'))[:200]))
    # 序号 → 通路原文 代换 + 覆盖校验
    all_paths = []
    for it in brief.get('items', []):
        all_paths.extend(it.get('paths') or it.get('cycles') or [])
    n = len(all_paths)
    used = set()
    for f in parsed.get('families', []):
        ids = f.get('members') or []
        f['members'] = [all_paths[i - 1] for i in ids
                        if isinstance(i, int) and 1 <= i <= n]
        f['member_ids'] = ids
        used.update(i for i in ids if isinstance(i, int) and 1 <= i <= n)
    parsed['coverage'] = '{}/{}'.format(len(used), n)
    if len(used) != n:
        parsed['uncovered_ids'] = sorted(
            set(range(1, n + 1)) - used)[:20]
    return parsed
