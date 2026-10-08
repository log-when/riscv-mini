#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""netlist_graph: 分层通道依赖图(sys 真值 + fir 结构标签)

管线:
  A 叶子级依赖图(Tile sys, 边带 kind=Data/Ctrl-inferred + 行号)
  B 节点分类(lo.fir inst 表 + 子模块 sys 端口/内部名; 实例端口/实例内部/tile布线/顶层端口)
  C 两层闭包(叶子粒度, 带 witness):
      第1层 布线: 端口→端口 只穿 tile 布线
      第2层 模块摘要: 子模块 sys 输入端口→输出端口
  D 通道图(bundle 通道键 + fwd/bwd 方向, witness + payload fields)
  E 性质驱动精化(root 钉住 → 敏感集收缩 → witness 字段展开)
  F 查询(cycles/paths/expand)

用法: python3 netlist_graph.py            # 跑验收用例
      作为库: from netlist_graph import NetlistGraph
"""
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from sys_parser import tokenize, ExprParser, _KINDS  # noqa: E402

BASE = _HERE.parent.parent          # riscv-mini/
RUN = BASE / 'test_run_dir'
TILE_SYS = RUN / 'Tile_should_pass/AGTileFlatProp.sys'
TILE_LOFIR = RUN / 'Tile_should_pass/AGTileFlatProp.lo.fir'
# 模块类型 → 高层 fir(bundle 结构) 与 sys(内部依赖)
MOD_FIR = {
    'AGICacheProp': BASE / 'AGICacheProp.fir',
    'AGDatapathProp': BASE / 'AGDatapathProp.fir',
    'AGControlProp': BASE / 'AGControlProp.fir',
    'AGMemArbiterProp': BASE / 'AGMemArbiterProp.fir',
}
MOD_SYS = {
    'AGICacheProp': RUN / 'ICache_should_pass/AGICacheProp.sys',
    'AGDatapathProp': RUN / 'Datapath_should_pass/AGDatapathProp.sys',
    'AGControlProp': RUN / 'Control_should_pass/ControlProp.sys',
    'AGMemArbiterProp': RUN / 'MemArbiter_should_pass/MemArbiterProp.sys',
}

# ---------------------------------------------------------------------------
# lo.fir: 模块块 + inst 表
# ---------------------------------------------------------------------------

def parse_lo_fir(path: Path) -> Dict[str, dict]:
    """→ {module: {'insts': {inst: type}, 'ports': {port: 'input'|'output'}}}"""
    mods = {}
    cur = None
    for line in open(path, encoding='utf-8', errors='ignore'):
        m = re.match(r'^  module (\S+) :', line)
        if m:
            cur = mods.setdefault(m.group(1), {'insts': {}, 'ports': {}})
            continue
        if cur is None:
            continue
        m = re.match(r'^\s{4}inst (\S+) of (\S+)', line)
        if m:
            cur['insts'][m.group(1)] = m.group(2)
            continue
        m = re.match(r'^\s+(input|output) (\S+) :', line)
        if m:
            cur['ports'][m.group(2)] = m.group(1)
    return mods


def inst_prefix_map(mods: Dict[str, dict], top: str) -> Dict[str, str]:
    """递归展开: 完整实例前缀 → 模块类型 (icache→AGICacheProp, dpath_csr→CSR...)"""
    table = {}

    def walk(mod_name, prefix):
        for iname, itype in mods.get(mod_name, {}).get('insts', {}).items():
            full = prefix + iname
            table[full] = itype
            walk(itype, full + '_')

    walk(top, '')
    return table


# ---------------------------------------------------------------------------
# 高层 fir: bundle 通道结构
# ---------------------------------------------------------------------------

def _parse_bundle(text: str):
    """'{ a : { b : T }, c : T }' → 树 dict {a: {b: None}, c: None}"""
    text = text.strip()
    assert text.startswith('{') and text.endswith('}')
    return _parse_fields(text[1:-1])


def _parse_fields(s: str) -> dict:
    tree = {}
    depth, start, name = 0, 0, None
    i = 0
    while i < len(s):
        c = s[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        elif c == ':' and depth == 0 and name is None:
            name = s[start:i].strip()
            start = i + 1
        elif c == ',' and depth == 0:
            if name is not None:
                key = name.split()[-1] if name.startswith('flip ') else name
                tree[key] = _parse_bundle(s[start:i]) \
                    if s[start:i].strip().startswith('{') else None
            name, start = None, i + 1
        i += 1
    if name is not None:
        key = name.split()[-1] if name.startswith('flip ') else name
        tree[key] = _parse_bundle(s[start:]) \
            if s[start:].strip().startswith('{') else None
    return tree


def module_channels(fir_path: Path) -> Dict[str, Tuple[str, str, bool]]:
    """高层 fir 顶层模块(circuit 同名)的 io bundle →
    {叶子flat名: (通道路径, 字段, is_payload)}; ready → 反向."""
    io_tree = None
    top = None          # circuit 名
    cur = None
    for line in open(fir_path, encoding='utf-8', errors='ignore'):
        m = re.match(r'^circuit (\S+) :', line)
        if m:
            top = m.group(1)
            continue
        m = re.match(r'^  module (\S+) :', line)
        if m:
            cur = m.group(1)
            continue
        if top is None or cur != top:
            continue
        line = re.sub(r'@\[.*\]\s*$', '', line.rstrip())
        m = re.match(r'^\s+(input|output)\s+(\S+)\s*:\s*(.+)$', line)
        if not m:
            continue
        name, typ = m.group(2), m.group(3).strip()
        if name == 'io' and typ.startswith('{'):
            io_tree = _parse_bundle(typ)
            break
    if io_tree is None:
        return {}
    chans = {}

    def walk(node, path, in_channel, channel):
        for fname, sub in node.items():
            p = path + [fname]
            is_handshake = fname in ('valid', 'ready')
            if in_channel:
                # payload 子树(bits.{...})继续下钻到叶子
                if sub and not is_handshake:
                    walk(sub, p, True, channel)
                    continue
                flat = 'io_' + '_'.join(path[1:] + [fname]) \
                    if path[0] == 'io' else '_'.join(path + [fname])
                chans[flat] = ('.'.join(channel), fname,
                               not is_handshake and fname != 'bits')
            else:
                # 未进通道: 若本子树含 valid/ready → 这一层是通道;
                # 纯叶子(无握手结构)自身成通道
                has_hs = sub and any(k in sub for k in ('valid', 'ready'))
                if not has_hs and not sub:
                    flat = 'io_' + '_'.join(p[1:]) if p[0] == 'io' \
                        else '_'.join(p)
                    chans[flat] = ('.'.join(p), fname, False)
                else:
                    walk(sub or {}, p, has_hs, p if has_hs else channel)

    walk(io_tree, ['io'], False, ['io'])
    return chans


def flat_channel_map(fir_path: Path) -> Dict[str, Tuple[str, str]]:
    """{flat叶名: (通道key, fwd|bwd)} — 通道key 去掉 io. 前缀, payload 字段并入 fwd"""
    raw = module_channels(fir_path)
    out = {}
    for flat, (chan, field, is_payload) in raw.items():
        c = chan[len('io.'):] if chan.startswith('io.') else chan
        out[flat] = (c, 'bwd' if field == 'ready' else 'fwd')
    return out


# ---------------------------------------------------------------------------
# 阶段 A: 叶子级依赖图(Tile sys) — 边带 kind + 行号
# ---------------------------------------------------------------------------

def build_leaf_graph(sys_path: Path):
    """→ fwd{src:{dst}}, edges{(src,dst): {'kind','line'}}"""
    fwd: Dict[str, Set[str]] = defaultdict(set)
    edges = {}
    lines = open(sys_path, encoding='utf-8', errors='ignore').readlines()

    def add(src, dst, kind, ln):
        fwd[src].add(dst)
        e = edges.get((src, dst))
        # Data 边优先保留(语义更强)
        if e is None or (e['kind'] != 'Data' and kind == 'Data'):
            edges[(src, dst)] = {'kind': kind, 'line': ln}

    cur_state = None
    for ln, line in enumerate(lines, 1):
        s = line.strip()
        if not s:
            continue
        tokens = tokenize(s)
        if not tokens:
            continue
        if tokens[0][0] == 'LBRACKET' and len(tokens) > 1 \
                and tokens[1][1] in ('init', 'next'):
            if cur_state:
                j = 2
                while j < len(tokens) and tokens[j][0] == 'RBRACKET':
                    j += 1
                ids_all = ExprParser(tokens, j).parse()
                ids_data = ExprParser(tokens, j, target=cur_state).parse()
                for rid in ids_all:
                    add(rid, cur_state,
                        'Data' if rid in ids_data else 'Ctrl-inferred', ln)
            continue
        if tokens[0][1] in _KINDS and len(tokens) > 1:
            kind_kw, name = tokens[0][1], tokens[1][1]
            cur_state = name if kind_kw == 'state' else None
            if kind_kw in ('input', 'state'):
                continue
            eq = None
            for j, (tt, _v) in enumerate(tokens):
                if tt == 'EQ':
                    eq = j + 1
                    break
            if eq is not None and eq < len(tokens):
                ids_all = ExprParser(tokens, eq).parse()
                ids_data = ExprParser(tokens, eq, target=name).parse()
                for rid in ids_all:
                    add(rid, name,
                        'Data' if rid in ids_data else 'Ctrl-inferred', ln)
        else:
            cur_state = None
    return dict(fwd), edges


# ---------------------------------------------------------------------------
# 主类
# ---------------------------------------------------------------------------

class NetlistGraph:
    def __init__(self, tile_sys=TILE_SYS, lo_fir=TILE_LOFIR,
                 mod_fir=None, mod_sys=None):
        mod_fir = mod_fir or MOD_FIR
        mod_sys = mod_sys or MOD_SYS
        self.fwd, self.edges = build_leaf_graph(Path(tile_sys))
        self.nodes = set(self.fwd) | {d for t in self.fwd.values() for d in t}

        # 阶段 B: 分类
        self.mods = parse_lo_fir(Path(lo_fir))
        self.inst2type = inst_prefix_map(self.mods, 'AGTileFlatProp')
        # 端口集(含方向)/内部名集 per 模块类型(来自子模块 sys)
        self.type_ports, self.type_internals = {}, {}
        self.type_dirs = {}      # {模块类型: {io端口: 'input'|'output'}}
        for t, p in mod_sys.items():
            ps, ins = set(), set()
            dirs = {}
            for line in open(p, encoding='utf-8', errors='ignore'):
                m = re.match(r'^(input|output)\s+(io_\S+)', line.strip())
                if m:
                    ps.add(m.group(2))
                    dirs[m.group(2)] = m.group(1)
                    continue
                m = re.match(r'^(node|state)\s+(\S+)', line.strip())
                if m:
                    ins.add(m.group(2).split('.')[0])
            self.type_ports[t], self.type_internals[t] = ps, ins
            self.type_dirs[t] = dirs
        self.cls = self._classify()
        # 通道映射 per 模块类型(来自高层 fir; 兜底尾缀规则)
        self.type_chan = {}
        for t, p in mod_fir.items():
            try:
                self.type_chan[t] = flat_channel_map(Path(p))
            except Exception:
                self.type_chan[t] = {}
        # 阶段 C
        self.wiring = self._wiring_closure()      # 第1层
        self.summaries = self._module_summaries(mod_sys)  # 第2层
        # 阶段 D
        self.chan_graph = self._channel_graph()

    # ---- B: 节点分类 -----------------------------------------------
    def _classify(self) -> Dict[str, tuple]:
        cls = {}
        prefixes = sorted(self.inst2type, key=len, reverse=True)
        for n in self.nodes:
            if n.startswith('io_'):
                cls[n] = ('topport', '', '', '')
                continue
            hit = None
            for pre in prefixes:
                if n.startswith(pre + '_'):
                    t = self.inst2type[pre]
                    rest = n[len(pre) + 1:]
                    if rest in self.type_ports.get(t, ()):
                        hit = ('port', pre, t, rest)
                    else:
                        base = rest.split('.')[0].split('_MPORT')[0]
                        base = re.sub(r'_\d+($|_)', r'[\*]\1', base) \
                            if re.match(r'^\w+_\d+$', base) else base
                        base = base.split('__')[0]
                        ins = self.type_internals.get(t, set())
                        if rest in ins or rest.split('.')[0] in ins:
                            hit = ('internal', pre, t, rest)
                    break
            if hit is None:
                # dpath_fe_reg_inst 等: 实例前缀已最短匹配, 余下按 tile 布线
                hit = ('tilewire', '', '', '')
            cls[n] = hit
        return cls

    # ---- C-1: 布线闭包 ---------------------------------------------
    def _wiring_closure(self) -> Dict[Tuple[str, str], list]:
        """端口→端口, 只穿 tilewire; → {(a,b): witness 中间点列表}"""
        ports = {n for n, c in self.cls.items() if c[0] == 'port'}
        out = {}

        def bfs(x):
            seen = {x}
            q = deque([(x, [])])
            while q:
                y, w = q.popleft()
                for z in self.fwd.get(y, ()):
                    if z in ports and z != x:
                        key = (x, z)
                        if key not in out or len(w) < len(out[key]):
                            out[key] = w
                    elif z not in seen and self.cls.get(z, ('tilewire',))[0] \
                            == 'tilewire':
                        seen.add(z)
                        q.append((z, w + [z]))

        for p in ports:
            if p in self.fwd:
                bfs(p)
        return out

    # ---- C-2: 模块摘要 ---------------------------------------------
    def _module_summaries(self, mod_sys) -> Dict[str, dict]:
        """每模块类型: {(in_port, out_port): {'kind','line'}} 从子模块 sys"""
        summaries = {}
        for t, p in mod_sys.items():
            fwd_t, edges_t = build_leaf_graph(Path(p))
            ps = self.type_ports[t]
            inputs = {x for x in ps if ('input ' + x) in
                      open(p, encoding='utf-8', errors='ignore').read(1 << 20)}
            outputs = ps - inputs
            summary = {}
            for i in inputs:
                if i not in fwd_t:
                    continue
                seen, q = {i}, deque([i])
                while q:
                    y = q.popleft()
                    for z in fwd_t.get(y, ()):
                        if z in outputs and z != i:
                            e = summary.setdefault(
                                (i, z), {'kind': 'Data', 'line': None})
                            et = edges_t.get((y, z), {})
                            if et.get('kind') == 'Data':
                                e['kind'], e['line'] = 'Data', et.get('line')
                            elif e['kind'] != 'Data':
                                e['kind'] = et.get('kind', 'Data')
                        elif z not in seen and z not in ps:
                            seen.add(z)
                            q.append(z)
            summaries[t] = summary
        return summaries

    # ---- D: 通道图 ---------------------------------------------------
    def port_channel(self, node: str) -> Optional[Tuple[str, str]]:
        """实例端口叶名 → (通道节点key, fwd|bwd)"""
        c = self.cls.get(node)
        if not c or c[0] != 'port':
            return None
        _, inst, t, port = c
        cmap = self.type_chan.get(t, {})
        if port in cmap:
            ch, d = cmap[port]
        else:
            ch0 = re.sub(r'(_valid|_ready)$|_bits.*$', '', port)
            ch = ch0 or port
            d = 'bwd' if port.endswith('_ready') else 'fwd'
        return '{}.{}.{}'.format(inst, ch, d), d

    def _channel_graph(self):
        """通道边: {src: {dst: {'wires': [叶子边], 'layers': set}}}"""
        g = defaultdict(dict)

        def add_edge(a, b, layer, leaf_edge=None):
            e = g[a].setdefault(b, {'layers': set(), 'leaf': []})
            e['layers'].add(layer)
            if leaf_edge:
                e['leaf'].append(leaf_edge)

        for (a, b), w in self.wiring.items():
            ca, cb = self.port_channel(a), self.port_channel(b)
            if ca and cb:
                add_edge(ca[0], cb[0], 'wire', (a, b))
        for t, summ in self.summaries.items():
            insts = [i for i, tt in self.inst2type.items() if tt == t
                     and '_' not in i[len(list(self.inst2type)[0]):] or True]
            # 每个该类型实例都挂摘要
            insts = [i for i, tt in self.inst2type.items() if tt == t]
            for inst in insts:
                for (i, o), info in summ.items():
                    ai = '{}_{}'.format(inst, i)
                    ao = '{}_{}'.format(inst, o)
                    ci, co = self.port_channel(ai), self.port_channel(ao)
                    if ci and co:
                        add_edge(ci[0], co[0],
                                 'module:' + t, (ai, ao))
        return {k: dict(v) for k, v in g.items()}

    # ---- E/F: 敏感集 / 环 / 展开 -------------------------------------
    def sensitivity(self, roots: List[str]) -> Set[str]:
        """通道图上 roots 正∩反可达 + roots 自身"""
        roots_c = [self.port_channel(r)[0] for r in roots
                   if self.port_channel(r)]
        F, q = set(), deque(roots_c)
        while q:
            x = q.popleft()
            for y in self.chan_graph.get(x, ()):
                if y not in F:
                    F.add(y)
                    q.append(y)
        Bw = defaultdict(set)
        for a, tgts in self.chan_graph.items():
            for b in tgts:
                Bw[b].add(a)
        B, q = set(), deque(roots_c)
        while q:
            x = q.popleft()
            for y in Bw.get(x, ()):
                if y not in B:
                    B.add(y)
                    q.append(y)
        return (F & B) | set(roots_c)

    def cycles(self, seed: str, max_len: Optional[int] = None,
               max_cycles: int = 200,
               exclude: Optional[List[str]] = None) -> List[List[str]]:
        """exclude: 不敏感信号子串表(如 ['abort']); 环中任一节点
        含子串即整环剔除。"""
        cs = []
        s = self.port_channel(seed)
        if not s:
            return cs
        start = s[0]
        excl = exclude or []
        if max_len is None:
            max_len = len(self.chan_graph) + 2

        def bad(node):
            return any(e in node for e in excl)

        def dfs(cur, path, onpath):
            if len(cs) >= max_cycles or len(path) > max_len:
                return
            for nxt in self.chan_graph.get(cur, ()):
                if nxt == start:
                    cs.append(list(path) + [start])
                    return
                if nxt in onpath or bad(nxt):
                    continue
                dfs(nxt, path + [nxt], onpath | {nxt})

        dfs(start, [start], {start})
        cs.sort(key=len)
        return cs

    def families(self, seed: str, max_len: Optional[int] = None, max_cycles: int = 100000,
                 exclude: Optional[List[str]] = None) -> List[dict]:
        """环 → 族(模块轨迹×回程通道)。返回 [{trace, ret, cycles, rep,
        variants: {位置: {候选}}}] 按族大小降序。"""
        cs = self.cycles(seed, max_len, max_cycles, exclude)

        def trace(c):
            seq = [x.split('.')[0] for x in c[:-1]]
            out = [seq[0]]
            for m in seq[1:]:
                if m != out[-1]:
                    out.append(m)
            return tuple(out[out.index('icache'):] +
                         out[:out.index('icache')]) if 'icache' in out \
                else tuple(out)

        def ret(c):
            return c[-2] if c[-2].endswith('.bwd') else '(fwd数据回)'

        grp = defaultdict(list)
        for c in cs:
            grp[(trace(c), ret(c))].append(c)
        out = []
        for (tr, rb), cycs in sorted(grp.items(), key=lambda kv: -len(kv[1])):
            rep = min(cycs, key=len)
            bypos = defaultdict(set)
            for c in cycs:
                for i, (a, b) in enumerate(zip(rep, c)):
                    if a != b:
                        bypos[i].add(b)
            out.append({'trace': tr, 'ret': rb, 'count': len(cycs),
                        'rep': rep,
                        'variants': {i: sorted(v) for i, v in bypos.items()}})
        return out

    def paths(self, src: str, dst: str, max_len: Optional[int] = None,
              exclude: Optional[List[str]] = None,
              limit: int = 100000) -> List[List[str]]:
        """src→dst 的【全部】简单通路(通道粒度), 按 max_len 截断防爆炸,
        limit 为硬上限(超过即停, 结果不完整)。"""
        s, t = self.port_channel(src), self.port_channel(dst)
        if not s or not t:
            return []
        start, target = s[0], t[0]
        excl = exclude or []
        if max_len is None:
            max_len = len(self.chan_graph) + 2
        if start == target:
            return [[start]]
        out = []

        def dfs(cur, path, onpath):
            if len(out) >= limit:
                return
            for nxt in self.chan_graph.get(cur, ()):
                if nxt == target:
                    out.append(list(path) + [target])
                    continue
                if len(path) >= max_len:
                    continue
                if nxt in onpath or any(e in nxt for e in excl):
                    continue
                dfs(nxt, path + [nxt], onpath | {nxt})

        dfs(start, [start], {start})
        out.sort(key=len)
        return out

    def leaf_witness(self, a: str, b: str) -> List[Tuple[str, str]]:
        """通道边 a→b 的叶子证据(端口对); 布线边展开途经节点, 模块边给摘要 I/O 对"""
        e = self.chan_graph.get(a, {}).get(b, {})
        return e.get('leaf', [])

    def edge_report(self, a: str, b: str) -> dict:
        return self.chan_graph.get(a, {}).get(b, {})

    def pairwise_paths(self, signals: List[str], max_len: Optional[int] = None,
                       exclude: Optional[List[str]] = None,
                       limit: int = 100000) -> dict:
        """信号集 S 的全序对【全部】简单通路矩阵(有向)。
        自对 "a -> a" = 过该信号的环; 同通道同方向信号合并为一点。"""
        pairs = []
        seen_ch = []
        for s in signals:
            c = self.port_channel(s)
            if c and c[0] not in seen_ch:
                seen_ch.append(c[0])
                pairs.append((s, c[0]))
        out = {}
        for s, c0 in pairs:
            out['{} -> {}'.format(s, s)] = self.cycles(
                s, max_len=max_len, max_cycles=limit, exclude=exclude)
            for t, c1 in pairs:
                if c0 == c1:
                    continue
                out['{} -> {}'.format(s, t)] = self.paths(
                    s, t, max_len=max_len, exclude=exclude, limit=limit)
        return out


# ---------------------------------------------------------------------------
def _acceptance():
    ng = NetlistGraph()
    from collections import Counter
    cnt = Counter(c[0] for c in ng.cls.values())
    print('[B] 节点分类:', dict(cnt))
    print('[B] 实例表:', {k: v for k, v in sorted(ng.inst2type.items())})
    print('[C1] 布线边:', len(ng.wiring))
    for t, s in ng.summaries.items():
        print('[C2] {} 摘要: {} 条 I/O 依赖'.format(t, len(s)))
    # 用例1: ICache 摘要含 req→resp
    summ = ng.summaries['AGICacheProp']
    hit = [(i, o) for (i, o) in summ
           if 'req_valid' in i and 'resp_valid' in o]
    print('[用例1] ICache req_valid→resp_valid 摘要:', hit[:3])
    # 用例2: 通道图最短环
    cs = ng.cycles('icache_io_cpu_resp_valid', max_len=6, max_cycles=500)
    print('[用例2] 通道环 {} 条, 最短:'.format(len(cs)))
    for c in cs[:3]:
        print('   ', ' -> '.join(c))
    # 用例3: 敏感集
    sens = ng.sensitivity(['icache_io_cpu_resp_valid',
                           'icache_io_cpu_req_valid'])
    has_nasti = [s for s in sens if 'nasti' in s]
    print('[用例3] 敏感集 {} 通道, 含 nasti: {}'.format(
        len(sens), sorted(has_nasti)[:6]))
    # 用例4: 环边报告
    if cs:
        c = cs[0]
        print('[用例4] 最短环边报告:')
        for a, b in zip(c, c[1:]):
            e = ng.edge_report(a, b)
            print('   {} -> {}  layers={}'.format(a, b, e.get('layers')))


if __name__ == '__main__':
    _acceptance()
