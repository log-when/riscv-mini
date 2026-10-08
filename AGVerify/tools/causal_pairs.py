#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""causal_pairs: 从 LTL 性质串静态提取因果信号对(前件→后件)

规则(静态, 无 LLM):
  A -> B            → (A, B)          蕴含
  A -> F B / X F B  → (A, B)          及时性(忽略时序算子)
  A U B             → (A, B)          直到
  合取/析取前件 G(a & b -> c) → (a,c),(b,c)
依赖 netlist_graph.port_channel 把信号名归一到通道。
"""
import re
from typing import List, Tuple, Optional

Pair = Tuple[str, str]

_TEMPORAL = r'(?:G|F|X)\s*'


def _split_top(s: str, op: str) -> Optional[List[str]]:
    """顶层(括号外)按 op 分割; 无则 None"""
    depth, parts, cur = 0, [], ''
    i = 0
    while i < len(s):
        c = s[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif depth == 0 and s.startswith(op, i):
            parts.append(cur)
            cur = ''
            i += len(op)
            continue
        cur += c
        i += 1
    parts.append(cur)
    return parts if len(parts) > 1 else None


def _balanced_strip(s: str) -> str:
    """若整体被一对平衡括号包裹则去一层"""
    if s.startswith('(') and s.endswith(')'):
        depth = 0
        for i, c in enumerate(s):
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0 and i < len(s) - 1:
                    return s      # 括号不只包住整体
        return s[1:-1].strip()
    return s


def _strip(s: str) -> str:
    s = s.strip()
    changed = True
    while changed:
        changed = False
        t = _balanced_strip(s)
        if t != s:
            s, changed = t, True
        t = re.sub(r'^' + _TEMPORAL, '', s).strip()
        if t != s:
            s, changed = t, True
    return s


def _atoms(s: str) -> List[str]:
    """表达式 → 原子信号(否定保留在边上不影响因果方向)"""
    s = _strip(s)
    parts = _split_top(s, ' & ') or _split_top(s, ' | ') or [s]
    out = []
    for p in parts:
        p = _strip(p).lstrip('!').strip()
        # 比较式 (a == b) 取左侧信号
        m = re.match(r'^([A-Za-z_]\w*)\s*(?:==|!=|<|>|<=|>=)', p)
        if m:
            out.append(m.group(1))
        elif re.match(r'^[A-Za-z_]\w*$', p):
            out.append(p)
    return out


def causal_pairs(formula: str) -> List[Pair]:
    """LTL 串 → 因果对列表(信号名层面, 未映射通道)"""
    out = []

    def walk(s):
        s = _strip(s)
        if not s:
            return
        imp = _split_top(s, '->')
        if imp:
            ante, cons = '->'.join(imp[:-1]), imp[-1]
            for a in _atoms(ante):
                for c in _atoms(cons):
                    if a != c:
                        out.append((a, c))
            walk(cons)
            return
        unt = _split_top(s, ' U ')
        if unt:
            for a in _atoms(unt[0]):
                for c in _atoms(unt[1]):
                    if a != c:
                        out.append((a, c))
            return
        # 顶层合取/析取: 逐项下钻
        parts = _split_top(s, ' & ') or _split_top(s, ' | ')
        if parts:
            for p in parts:
                walk(p)

    walk(formula)
    seen, res = set(), []
    for p in out:
        if p not in seen:
            seen.add(p)
            res.append(p)
    return res


def channel_pairs(formula: str, signals: List[Tuple[str, str]],
                  ng=None) -> List[Tuple[str, str]]:
    """性质 + cha_verify signals(别名,路径,编号) + NetlistGraph
    → [(flat信号A, flat信号B)]。
    路径支持实例限定(icache.io.cpu.req.valid)与模块相对(io.cpu.req.valid,
    后缀匹配解析端口节点, 多实例命中全部保留)。"""
    alias2flat = {}
    for alias, path, _n in signals:
        flat = path.replace('.', '_')
        alias2flat[alias] = flat
        alias2flat[flat] = flat

    def resolve(name):
        flat = alias2flat.get(name) or name
        if ng is None:
            return [flat]
        if ng.port_channel(flat):
            return [flat]
        hits = sorted(n for n, c in ng.cls.items()
                      if c[0] == 'port' and n.endswith('_' + flat))
        return hits or [flat]

    res = []
    for a, b in causal_pairs(formula):
        for fa in resolve(a):
            for fb in resolve(b):
                if ng is not None:
                    ca, cb = ng.port_channel(fa), ng.port_channel(fb)
                    if not ca or not cb or ca[0] == cb[0]:
                        continue
                res.append((fa, fb))
    return res
