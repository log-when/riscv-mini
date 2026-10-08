#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通路简报流水线: 静态全量通路 → 格式化 → LLM 语义总结 → decomposer 输入

用法: python3 gen_path_brief.py [性质名] [信号1 信号2 ...]
默认: F response 义务链 (req/resp/ar/r)。
产物(AGVerify/out/<性质名>/):
  path_brief.md     静态通路数据(全量, 含族压缩)
  path_summary.json LLM 语义总结(族命名/伪环标注/假设落点)
"""
import sys
import json
from collections import defaultdict
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / 'tools'))
sys.path.insert(0, str(_HERE.parent / 'agents'))
from netlist_graph import NetlistGraph  # noqa: E402

DEFAULT_PROP = {
    'name': 'F_response',
    'signals': ['icache_io_cpu_req_valid', 'icache_io_cpu_resp_valid',
                'icache_io_nasti_ar_valid', 'icache_io_nasti_r_valid'],
}


def path_families(paths):
    """通路按模块轨迹聚族; 返回 [{trace, count, rep, variants}]"""
    def trace(p):
        seq = [x.split('.')[0] for x in p]
        out = [seq[0]]
        for m in seq[1:]:
            if m != out[-1]:
                out.append(m)
        return tuple(out)

    grp = defaultdict(list)
    for p in paths:
        grp[trace(p)].append(p)
    out = []
    for tr, ps in sorted(grp.items(), key=lambda kv: -len(kv[1])):
        rep = min(ps, key=len)
        bypos = defaultdict(set)
        for p in ps:
            for i, (a, b) in enumerate(zip(rep, p)):
                if a != b:
                    bypos[i].add(b)
        out.append({'trace': '->'.join(tr), 'count': len(ps),
                    'hops': len(rep) - 1, 'rep': rep,
                    'variants': {i: sorted(v) for i, v in bypos.items()}})
    return out


def gen_brief(ng, signals, max_len=None, llm_top_fams=8):
    """全量通路 → (LLM 浓缩简报, 全量结构化数据)。
    LLM 简报每对只列 top-N 族(按条数) + 其余族统计, 全量在 structured。"""
    m = ng.pairwise_paths(signals, max_len=max_len, limit=1000000)
    L = ['# 通路简报(静态)\n',
         '信号集: {}\n'.format(', '.join(signals)),
         '图例: 通道节点 <实例>.<通道>.[fwd|bwd]; fwd=请求/数据正向, '
         'bwd=ready 反压; 边来源 wire=顶层布线(环境), module:X=模块内依赖(设计)',
         '每对列条数最多的前 {} 族(其余族以统计行概括); 通路为全部简单通路, 无长度截断\n'.format(llm_top_fams)]
    structured = {}
    for key in sorted(m):
        ps = m[key]
        fams = path_families(ps)
        structured[key] = {'count': len(ps), 'families': [
            {'trace': f['trace'], 'count': f['count'], 'hops': f['hops'],
             'rep': f['rep'], 'variants': f['variants']} for f in fams]}
        L.append('## {} —— {} 条通路, {} 个族\n'.format(key, len(ps), len(fams)))
        shown = fams[:llm_top_fams]
        rest = fams[llm_top_fams:]
        for f in shown:
            L.append('- 族 `{}` ({}条, {}跳): {}'.format(
                f['trace'], f['count'], f['hops'], ' -> '.join(f['rep'])))
            nv = 0
            for i, cands in sorted(f['variants'].items()):
                if nv >= 6:
                    L.append('    变化点其余 {} 处省略'.format(
                        len(f['variants']) - nv))
                    break
                L.append('    变化[{}] `{}` ∈ {}'.format(
                    i, f['rep'][i], ' | '.join(sorted(set(cands))[:5])))
                nv += 1
        if rest:
            L.append('- (其余 {} 族共 {} 条, 多为上述骨架的更长组合; '
                     '完整清单见 path_brief.json)'.format(
                         len(rest), sum(f['count'] for f in rest)))
        L.append('')
    return '\n'.join(L), structured


SYSTEM_PROMPT = """你是硬件协议分析专家。输入是 SoC 通道依赖图的通路简报:
- 图的节点是协议通道(如 icache.nasti.ar.fwd), fwd=请求/数据方向, bwd=ready反压方向
- 每个信号对列出全部简单通路, 已按模块轨迹聚族(变化点=族内可替换的通道)
- riscv-mini 结构: icache/dcache(带miss状态机的Cache) 共享 nasti 总线, arb 仲裁, dpath 五级流水

任务: 为每对信号输出族的语义总结, 供 LLM 分解器(decomposer)做 assume-guarantee 分解时参考。

输出 JSON:
{
 "pairs": [{"pair": "a -> b", "summary": "一句话语义",
            "families": [{"trace": "...", "name": "族语义名(如 写回+二次访存)",
                          "obligation": "环境义务|设计义务|混合",
                          "note": "可疑/伪环备注(无则空)"}]}],
 "assumption_hints": ["建议的假设落点, 如 'F nastiReadReqReady 应挂在 ar.bwd 回程'"],
 "decomposer_advice": ["给分解器的具体建议(2-5条)"]
}
判定规则: 回程走 bwd(ready) → 环境公平性义务; 回程走 r.fwd → 数据及时性义务;
通路不出模块 → 设计义务; 同骨架多条仅 nasti 出口不同 → 参数化为一族, 不要逐条罗列。"""


def main():
    prop = DEFAULT_PROP
    if len(sys.argv) > 2:
        prop = {'name': sys.argv[1], 'signals': sys.argv[2:]}
    out_dir = _HERE.parent / 'out' / prop['name']
    out_dir.mkdir(parents=True, exist_ok=True)

    ng = NetlistGraph()
    brief, structured = gen_brief(ng, prop['signals'])
    (out_dir / 'path_brief.md').write_text(brief, encoding='utf-8')
    (out_dir / 'path_brief.json').write_text(
        json.dumps(structured, ensure_ascii=False, indent=2), encoding='utf-8')
    print('[静态] 通路简报 →', out_dir / 'path_brief.md',
          '({} 字节)'.format(len(brief)))

    from llm import chat
    r = chat('summarizer', SYSTEM_PROMPT,
             {'property': prop['name'],
              '__text__': {'通路简报': brief}}, json_mode=True)
    summary = r.get('parsed')
    if summary is None:
        print('[LLM] 解析失败, 原文:',
              str(r.get('content'))[:500])
        return 1
    (out_dir / 'path_summary.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print('[LLM] 语义总结 →', out_dir / 'path_summary.json')

    # decomposer 输入格式: 摘要化的建议清单
    advice = {
        'property': prop['name'],
        'assumption_hints': summary.get('assumption_hints', []),
        'decomposer_advice': summary.get('decomposer_advice', []),
        'pair_family_count': {k: v['count'] for k, v in structured.items()},
    }
    (out_dir / 'decomposer_input.json').write_text(
        json.dumps(advice, ensure_ascii=False, indent=2), encoding='utf-8')
    print('[产物] decomposer 输入 →', out_dir / 'decomposer_input.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
