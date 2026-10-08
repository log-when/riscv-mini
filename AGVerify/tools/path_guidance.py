#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""path_guidance: 义务定位器 + 通路引导简报(供 decomposer/critic 消费)

流程:
  gate(module, formula, signals)     静态决策表(微秒级)
    in→out 在摘要   → local    (本模块直接兑现)
    in→out 不在摘要 → trivial  (模块内自然满足, 前件碰不到后件)
    in→in  同源模块  → transfer (义务转移, port_map 给出映射)
    in→in  顶层端口  → env     (真环境假设)
    其余(out→in/跨模块/混合) → global
    单信号          → cycles
  brief(gate结果)  对 global/cycles 项生成静态简报(端口路径落点)
  classify(...)    调 path_classifier agent 做族语义归类(带缓存)

guidance(node_ctx) = 完整入口, dispatcher 直接调用。
"""
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

_HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / 'agents'))
from causal_pairs import causal_pairs  # noqa: E402


class PathGuidance:
    def __init__(self, cache_path: Optional[Path] = None):
        self._ng = None
        self._mem = {}                      # (module, formula hash) → 结果
        self.cache_path = Path(cache_path) if cache_path else \
            _HERE.parent / 'out' / 'guidance_cache.json'
        self._disk = {}
        try:
            if self.cache_path.exists():
                self._disk = json.loads(
                    self.cache_path.read_text(encoding='utf-8'))
        except Exception:
            self._disk = {}

    # ---- 惰性图 ----
    @property
    def ng(self):
        if self._ng is None:
            from netlist_graph import NetlistGraph
            self._ng = NetlistGraph()
        return self._ng

    def available(self) -> bool:
        """图数据是否可用(其他设计零影响降级)"""
        try:
            _ = self.ng.nodes
            return True
        except Exception:
            return False

    # ---- 工具 ----
    def _module_type(self, module: str) -> Optional[str]:
        """任务模块名(ICache/DCache/...) → 图模块类型(AGICacheProp/...)"""
        t = 'AG' + module + 'Prop'
        if t in self.ng.summaries:
            return t
        return None

    def _local_ports(self, module: str) -> Dict[str, str]:
        """{flat端口名: 方向} (本模块端口, 无实例前缀)"""
        t = self._module_type(module)
        return self.ng.type_dirs.get(t, {}) if t else {}

    def _resolve(self, name: str, alias2flat: Dict[str, str],
                 module: str) -> Optional[str]:
        """性质信号名 → 本模块 flat 端口名"""
        flat = alias2flat.get(name) or name
        lp = self._local_ports(module)
        if flat in lp:
            return flat
        return None

    def _drivers_module(self, port_flat: str, module: str) -> Optional[str]:
        """本模块输入端口由哪个模块驱动(顶层端口→'__env__')"""
        # 找到图节点: <inst>_<port>, inst 的类型是本模块
        t = self._module_type(module)
        me = None
        for inst, it in self.ng.inst2type.items():
            if it == t and '_' not in inst:
                if inst + '_' + port_flat in self.ng.cls:
                    me = inst + '_' + port_flat
                    break
        if me is None:
            return '__pruned__'   # 死线: sys 生成时被裁剪(无扇出)
        for (a, b) in self.ng.wiring:
            if b == me:
                ca = self.ng.cls.get(a)
                if ca and ca[0] == 'topport':
                    return '__env__'
                if ca and ca[0] == 'port':
                    return ca[1]          # 驱动实例名
        return '__env__'                  # 无布线边驱动 → 视为环境

    # ---- 决策表 ----
    def gate(self, module: str, formula: str,
             signals: Dict[str, Dict]) -> Dict:
        """signals: cha_verify 形式 {别名: {module, port/expr}}。
        返回 {pairs: [...], singles: [...], notes: [...]}"""
        alias2flat = {}
        for alias, s in (signals or {}).items():
            port = s.get('port')
            if port:
                alias2flat[alias] = port.replace('.', '_')
        lp = self._local_ports(module)
        t = self._module_type(module)
        summ = self.ng.summaries.get(t, {}) if t else {}

        pairs_out = []
        for a, b in causal_pairs(formula):
            fa = self._resolve(a, alias2flat, module)
            fb = self._resolve(b, alias2flat, module)
            if fa is None or fb is None:
                pairs_out.append({'pair': (a, b), 'verdict': 'global',
                                  'why': '信号不在本模块端口或不可解析'})
                continue
            da, db = lp.get(fa), lp.get(fb)
            if da == 'input' and db == 'output':
                in_sum = (fa, fb) in summ
                pairs_out.append({
                    'pair': (a, b), 'verdict':
                        'local' if in_sum else 'trivial',
                    'why': '输入→输出' + (', 模块摘要含此依赖'
                                           if in_sum else
                                           ', 模块内无此依赖(前件碰不到后件)')})
            elif da == 'output' and db == 'input':
                pairs_out.append({'pair': (a, b), 'verdict': 'global',
                                  'why': '输出→输入: 环境反馈环'})
            elif da == 'input' and db == 'input':
                ma = self._drivers_module(fa, module)
                mb = self._drivers_module(fb, module)
                if '__pruned__' in (ma, mb):
                    pairs_out.append({
                        'pair': (a, b), 'verdict': 'env',
                        'why': '信号在全局图中被裁剪(无扇出/死线): '
                               '模块观测不到, 纯环境契约'})
                elif ma and mb and ma == mb and ma != '__env__':
                    pairs_out.append({
                        'pair': (a, b), 'verdict': 'transfer', 'to': ma,
                        'why': '两输入同由 {} 驱动, 义务转移'.format(ma)})
                elif ma == '__env__' or mb == '__env__':
                    pairs_out.append({
                        'pair': (a, b), 'verdict': 'env',
                        'why': '由顶层环境驱动: 真环境假设'})
                else:
                    pairs_out.append({
                        'pair': (a, b), 'verdict': 'global',
                        'why': '输入由不同模块驱动({} vs {})'.format(ma, mb)})
            else:   # out→out
                in_sum = (fa, fb) in summ
                pairs_out.append({
                    'pair': (a, b), 'verdict': 'local' if in_sum else 'trivial',
                    'why': '输出→输出' + ('' if in_sum else ', 模块内无依赖')})

        # 单信号: 公式只有一个原子信号
        singles = []
        cps = causal_pairs(formula)
        all_atoms = set()
        for a, b in cps:
            all_atoms.add(a)
            all_atoms.add(b)
        if not cps:
            # 提取全部原子(无因果结构, 如 F sig / G sig)
            for m in re.findall(r'[A-Za-z_]\w*', formula):
                if m not in ('G', 'F', 'X', 'U', 'and', 'or', 'not'):
                    all_atoms.add(m)
        if len(all_atoms) == 1:
            singles.append({'signal': next(iter(all_atoms)),
                            'verdict': 'cycles',
                            'why': '单信号活性: 检查回馈环停滞'})
        return {'pairs': pairs_out, 'singles': singles}

    # ---- 通道 → 端口路径(供 LLM 写 io.*) ----
    def _chan_to_ports(self, module: str = None) -> Dict[str, List[str]]:
        """{模块相对通道key: [io.* 路径]}。
        module=None 时合并所有模块类型的通道表(跨模块通道反查用)。"""
        types = ([self._module_type(module)] if module
                 else list(self.ng.type_chan.keys()))
        out = defaultdict(list)
        for t in types:
            for flat, (ch, d) in self.ng.type_chan.get(t, {}).items():
                pretty = 'io.' + flat[len('io_'):].replace('_', '.') \
                    if flat.startswith('io_') else flat
                out['{}.{}'.format(ch, d)].append(
                    '{}[{}]'.format(pretty, self._module_name(t) or t))
        return dict(out)

    def _module_name(self, t: str) -> Optional[str]:
        """AGICacheProp → ICache(用于端口标注归属)"""
        return t[2:-4] if t.startswith('AG') and t.endswith('Prop') else None

    def _inst_of_module(self, module: str) -> Optional[str]:
        """任务模块 → 图实例名(顶层实例)"""
        t = self._module_type(module)
        if not t:
            return None
        for inst, it in self.ng.inst2type.items():
            if it == t and '_' not in inst:
                return inst
        return None

    # ---- 动态头部通路: 按总数比例截断(上近似) ----
    def _head_paths(self, full_a, full_b, frac=0.01,
                    limit=100000) -> List[List[str]]:
        """全量计数 → 找最小 max_len 使保留数 ≥ ceil(frac*总数)。
        保留的是最短头部通路(义务主干), 长尾多回合组合被丢弃。"""
        full = self.ng.paths(full_a, full_b, max_len=None, limit=limit)
        target = max(1, -(-int(len(full) * frac) // 1))
        if len(full) <= target:
            return full
        lo, hi = 1, max(len(x) for x in full) - 1
        best = full
        for ml in range(1, hi + 1):
            kept = self.ng.paths(full_a, full_b, max_len=ml, limit=limit)
            if len(kept) >= target:
                return kept
        return full

    # ---- 静态简报(global/cycles 项) ----
    def brief(self, module: str, gate_res: Dict, signals: Dict,
              top_fams: int = 3, max_paths_per_pair: int = 20000
              ) -> Dict:
        """对 global/cycles 项生成通路/环族简报(通道+端口双表达)。"""
        alias2flat = {}
        for alias, s in (signals or {}).items():
            port = s.get('port')
            if port:
                alias2flat[alias] = port.replace('.', '_')
        inst = self._inst_of_module(module)
        all_c2p = self._chan_to_ports()      # 全类型合并表(跨模块反查)
        items = []

        def chan_repr(ch):
            # 全通道键带实例前缀(arb.icache.ar.fwd) → 去前缀查模块相对键
            key = ch.split('.', 1)[1] if ch.count('.') >= 2 else ch
            ports = all_c2p.get(key, [])
            return '{} ({})'.format(ch, ports[0] if ports else '?')

        for pr in gate_res.get('pairs', []):
            if pr['verdict'] != 'global':
                continue
            a, b = pr['pair']
            fa, fb = alias2flat.get(a) or a, alias2flat.get(b) or b
            full_a = self._rep_of((inst + '_' + fa) if inst else fa)
            full_b = self._rep_of((inst + '_' + fb) if inst else fb)
            ps = self._head_paths(full_a, full_b,
                                  limit=max_paths_per_pair)
            fams = _path_families(ps)
            items.append({
                'pair': list(pr['pair']), 'why': pr.get('why'),
                'path_count': len(ps),
                'trace_family_count': len(fams),
                'paths': [' -> '.join(chan_repr(x) for x in p)
                          for p in ps],
                'static_families': [
                    {'trace': f['trace'], 'count': f['count'],
                     'hops': f['hops'],
                     'rep_chan': [chan_repr(x) for x in f['rep']]}
                    for f in fams[:top_fams]]})

        for sg in gate_res.get('singles', []):
            if sg['verdict'] != 'cycles':
                continue
            name = sg['signal']
            flat = alias2flat.get(name) or name
            full = self._rep_of((inst + '_' + flat) if inst else flat)
            cs = self._head_cycles(full)
            items.append({
                'signal': name, 'cycle_count': len(cs),
                'cycles': [' -> '.join(chan_repr(x) for x in c)
                           for c in cs]})

        # 落点建议(静态规则)
        hints = []
        for it in items:
            seqs = it.get('paths') or it.get('cycles') or []
            if any('.bwd (' in s for s in seqs[:50]):
                hints.append('通路集含 ready 反压(bwd) 回程 → '
                             '考虑停滞公平性假设 F <ready信号>')
            if any('.r.fwd (' in s for s in seqs[:50]):
                hints.append('通路集含 r.fwd 数据回程 → '
                             '考虑及时性假设 fire -> X F <valid>')
        return {'items': items, 'assumption_hints': hints[:6]}

    def _head_cycles(self, full: str, frac: float = 0.01,
                     max_cycles: int = 300) -> List[List[str]]:
        """环的头部截断: 最短 frac 比例(上近似), 上限 max_cycles 条"""
        cs = self.ng.cycles(full, max_len=None, max_cycles=1000000)
        target = max(1, int(len(cs) * frac))
        return cs[:min(max(target, 1), max_cycles)]


    # ---- 信号等价类(纯布线直连 = 同一电气网络) ----
    def _sig_reps(self) -> Dict[str, str]:
        """并查集 ng.wiring 边 → {信号名: 类代表(类内字典序最小)}。
        只合并布线直连端口(无逻辑), 不合并任何通道级推导。"""
        if hasattr(self, '_reps'):
            return self._reps
        parent = {}

        def find(x):
            while parent.get(x, x) != x:
                parent[x] = parent.get(parent[x], parent[x])
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)

        def _inst_of(n):
            c = self.ng.cls.get(n)
            # ('port', inst, ...) → inst; topport → '__top__'; 其它不参与
            if c and c[0] == 'port':
                return c[1]
            if c and c[0] == 'topport':
                return '__top__'
            return None

        for (a, b) in self.ng.wiring:
            ia, ib = _inst_of(a), _inst_of(b)
            # 防误并: 只合并跨实例(或顶层)的真布线边;
            # 同实例端口直连边是模块内部依赖(路由逻辑压缩), 不是同一网络
            if ia is None or ib is None or ia == ib:
                continue
            parent.setdefault(a, a)
            parent.setdefault(b, b)
            union(a, b)
        groups = {}
        for n in parent:
            groups.setdefault(find(n), []).append(n)
        reps = {}
        for r, members in groups.items():
            rep = min(members)
            for m in members:
                reps[m] = rep
        self._reps = reps
        return reps

    def _rep_of(self, full_name: str) -> str:
        """实例限定名 → 等价类代表(不在任何类则原样返回)。"""
        try:
            return self._sig_reps().get(full_name, full_name)
        except Exception:
            return full_name

    def _pair_cache_key(self, module: str, formula: str,
                        signals: Dict) -> Optional[str]:
        """因果对(经信号等价类规范化) → 缓存键。
        失败返回 None(调用方降级用公式键)。"""
        try:
            alias2flat = {}
            for alias, s in (signals or {}).items():
                port = s.get('port')
                if port:
                    alias2flat[alias] = port.replace('.', '_')
            inst = self._inst_of_module(module)
            cps = causal_pairs(formula)
            if cps:
                def full(x):
                    f = alias2flat.get(x) or x
                    return self._rep_of(
                        (inst + '_' + f) if inst else f)
                ks = tuple(sorted(tuple(sorted((full(a), full(b))))
                                  for a, b in cps))
                kind = 'PAIR'
            else:
                import re as _re
                atoms = sorted({m for m in
                                _re.findall(r'[A-Za-z_]\w*', formula)
                                if m not in ('G', 'F', 'X', 'U')})
                ks = tuple(self._rep_of(
                    (inst + '_' + (alias2flat.get(a) or a)) if inst
                    else (alias2flat.get(a) or a)) for a in atoms)
                kind = 'SIG'
            return '{}|{}'.format(kind, hashlib.md5(
                repr(ks).encode('utf-8')).hexdigest()[:12])
        except Exception:
            return None

    # ---- 完整入口(含 LLM 归类与缓存) ----
    def guidance(self, module: str, formula: str, signals: Dict) -> Dict:
        """dispatcher 入口: gate → brief → (LLM 归类, 缓存)。
        任何失败降级为 {'error': ...}, 调用方按缺省处理。"""
        key = self._pair_cache_key(module, formula, signals) \
            or 'f|{}|{}'.format(module, hashlib.md5(
                formula.encode('utf-8')).hexdigest()[:12])
        if key in self._mem:
            return self._mem[key]
        if key in self._disk:
            self._mem[key] = self._disk[key]
            return self._disk[key]
        try:
            g = self.gate(module, formula, signals)
            b = self.brief(module, g, signals)
        except Exception as e:
            return {'error': 'gate/brief 失败: {}'.format(e)}
        result = {'gate': g, 'brief': b}
        # 草稿目录: 丢给 agent 的输入可读存档
        draft_dir = _HERE.parent / 'out' / 'drafts'
        try:
            draft_dir.mkdir(parents=True, exist_ok=True)
            stem = '{}_{}'.format(module, key.split('|')[1])
            from path_classifier import paths_text
            (draft_dir / (stem + '_agent_input.md')).write_text(
                '# {}\n{}\n\n公式: {}\n\n{}'.format(
                    module, '=' * 60, formula, paths_text(b)),
                encoding='utf-8')
        except Exception:
            draft_dir = None
        # LLM 归类(需要且有 global/cycles 项才调)
        need_llm = (any(p['verdict'] == 'global' for p in g['pairs'])
                    or any(s['verdict'] == 'cycles' for s in g['singles']))
        if need_llm and b.get('items'):
            try:
                from path_classifier import classify
                smap = {a: {'module': s.get('module', module),
                            'port': s.get('port', a)}
                        for a, s in (signals or {}).items()}
                result['classified'] = classify(module, formula, g, b, smap)
            except Exception as e:
                result['classify_error'] = str(e)
        if draft_dir is not None and 'classified' in result:
            try:
                c = result['classified']
                L = ['# agent 返回 — {} | {}'.format(module, formula), '']
                for f in c.get('families', []):
                    L.append('## [{}] {} ({})'.format(
                        f.get('obligation'), f.get('name'),
                        len(f.get('members', []))))
                    if f.get('note'):
                        L.append('')
                        L.append(f['note'])
                    L.append('')
                (draft_dir / (stem + '_agent_output.md')).write_text(
                    '\n'.join(L), encoding='utf-8')
            except Exception:
                pass
        self._mem[key] = result
        self._disk[key] = result
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(
                json.dumps(self._disk, ensure_ascii=False, indent=1),
                encoding='utf-8')
        except Exception:
            pass
        return result

    def ctx_block(self, module: str, formula: str, signals: Dict) -> Optional[Dict]:
        """生成 decomposer ctx 的 通路引导 块; 不可用返回 None。"""
        if not self.available():
            return None
        r = self.guidance(module, formula, signals)
        if 'error' in r:
            return None
        g = r['gate']
        block = {
            'signal_map': {a: s.get('port', a)
                           for a, s in (signals or {}).items()},
            'verdicts': [{'pair': list(p['pair']), 'verdict': p['verdict'],
                          'to': p.get('to'), 'why': p['why']}
                         for p in g['pairs']]
                       + [{'signal': s['signal'], 'verdict': s['verdict']}
                          for s in g['singles']],
        }
        if 'classified' in r:
            c = r['classified']
            fams = c.get('families') or []
            if fams:
                # ctx 放 LLM 返回的完整归类信息(name/obligation/note/
                # member_ids 序号), 不含代换后的通路原文(留 drafts 审计)
                block['families'] = [
                    {'name': f.get('name'),
                     'obligation': f.get('obligation'),
                     'note': f.get('note'),
                     'path_count': len(f.get('members', [])),
                     'member_ids': f.get('member_ids', [])}
                    for f in fams]
                if c.get('coverage'):
                    block['coverage'] = c['coverage']
        if not block['verdicts'] and 'families' not in block:
            return None
        # 草稿: decomposer 实际收到的块
        try:
            import json as _json
            stem = '{}_{}'.format(module, hashlib.md5(
                formula.encode('utf-8')).hexdigest()[:12])
            d = _HERE.parent / 'out' / 'drafts'
            d.mkdir(parents=True, exist_ok=True)
            (d / (stem + '_ctx_block.json')).write_text(
                _json.dumps(block, ensure_ascii=False, indent=1),
                encoding='utf-8')
            # 可读报告(md): 公式/signal_map/verdicts/各族完整 members
            L = ['# 通路引导 ctx 块可读报告', '',
                 '公式: {} ({})'.format(formula, module),
                 'signal_map: ' + _json.dumps(
                     block.get('signal_map', {}), ensure_ascii=False), '']
            L.append('## verdicts')
            for v in block.get('verdicts', []):
                if 'pair' in v:
                    L.append('- {} → {}: {} ({})'.format(
                        v['pair'][0], v['pair'][1],
                        v['verdict'], v.get('why', '')))
                else:
                    L.append('- 单信号 {}: {}'.format(
                        v.get('signal'), v['verdict']))
            L.append('')
            tot = 0
            for f in block.get('families', []):
                mem = f.get('members', [])
                tot += len(mem)
                L.append('## [{}] {} ({} 条)'.format(
                    f.get('obligation'), f.get('name'), len(mem)))
                L.append('')
                L.append('note: ' + (f.get('note') or ''))
                L.append('')
                L.append('members:')
                for mid, m in zip(f.get('member_ids', range(len(mem))), mem):
                    L.append('  {}. {}'.format(mid, m))
                L.append('')
            L.append('覆盖校验: 共 {} 条通路'.format(tot))
            (d / (stem + '_ctx_report.md')).write_text(
                '\n'.join(L), encoding='utf-8')
        except Exception:
            pass
        return block


def _path_families(paths):
    """通路按模块轨迹聚族"""
    from collections import defaultdict

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
            for i, (x, y) in enumerate(zip(rep, p)):
                if x != y:
                    bypos[i].add(y)
        out.append({'trace': '->'.join(tr), 'count': len(ps),
                    'hops': len(rep) - 1, 'rep': rep,
                    'variants': {i: sorted(v) for i, v in bypos.items()}})
    return out


# ---------------------------------------------------------------------------
# 兼容导入守卫
# ---------------------------------------------------------------------------
try:
    from llm import chat  # noqa: F401,E402
    _LLM_OK = True
except Exception:
    _LLM_OK = False
