#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sig_equiv: 信号等价类规范化服务(全框架共用, 单一实现)

档位契约(见 memory/project_signal_equiv.md):
  L1 语法归一(空白)                      — 保语义
  L2 信号等价类规范化(纯布线直连重命名)   — 保语义(双射重命名), KB 复用可用
  L3 因果对抽象(忽略公式形态)            — 不保语义, 仅 neg_kb/缓存键可用

任何失败(图缺失/解析异常)降级为 L1, 绝不抛异常到调用方。
"""
import re
from pathlib import Path
from typing import Dict, Optional

_HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# 等价类(惰性单例; 与 PathGuidance._sig_reps 同规则: 跨实例纯布线才合并)
# ---------------------------------------------------------------------------

_REPS = None          # {实例限定flat名: 类代表}


def _build_reps() -> Dict[str, str]:
    from netlist_graph import NetlistGraph
    ng = NetlistGraph()
    parent = {}

    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x])
            x = parent[x]
        return x

    def inst_of(n):
        c = ng.cls.get(n)
        if c and c[0] == 'port':
            return c[1]
        if c and c[0] == 'topport':
            return '__top__'
        return None

    for (a, b) in ng.wiring:
        ia, ib = inst_of(a), inst_of(b)
        if ia is None or ib is None or ia == ib:
            continue          # 同实例端口直连 = 模块内部依赖, 非布线
        parent.setdefault(a, a)
        parent.setdefault(b, b)
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    groups = {}
    for n in parent:
        groups.setdefault(find(n), []).append(n)
    return {m: min(members) for members in groups.values() for m in members}


def reps() -> Dict[str, str]:
    global _REPS
    if _REPS is None:
        try:
            _REPS = _build_reps()
        except Exception:
            _REPS = {}        # 降级: 无等价类, L2 == L1
    return _REPS


def rep_of(name: str) -> str:
    return reps().get(name, name)


# ---------------------------------------------------------------------------
# 公式规范化
# ---------------------------------------------------------------------------

_ATOM_RE = re.compile(r'[A-Za-z_]\w*')
_RESERVED = {'G', 'F', 'X', 'U', 'and', 'or', 'not', 'true', 'false'}


def _alias_map(signals: Optional[Dict]) -> Dict[str, str]:
    """{别名: 实例限定 flat 名}——需要 module→实例前缀"""
    out = {}
    if not signals:
        return out
    inst = _inst_of_module(next(iter(signals.values()), {})
                           .get('module', ''))
    for alias, s in signals.items():
        port = s.get('port')
        if not port:
            continue
        flat = port.replace('.', '_')
        m = s.get('module')
        pre = _inst_of_module(m) if m else inst
        out[alias] = (pre + '_' + flat) if pre else flat
        out[flat] = out[alias]
    return out


def _inst_of_module(module: str) -> Optional[str]:
    if not module:
        return None
    try:
        from netlist_graph import NetlistGraph
        ng = _ng()
        t = 'AG' + module + 'Prop'
        for inst, it in ng.inst2type.items():
            if it == t and '_' not in inst:
                return inst
    except Exception:
        pass
    return None


_NG = None


def _ng():
    global _NG
    if _NG is None:
        from netlist_graph import NetlistGraph
        _NG = NetlistGraph()
    return _NG


def norm_L2(formula: str, signals: Optional[Dict]) -> str:
    """公式原子 → 等价类代表名(保语义的双射重命名), 再语法归一。"""
    amap = _alias_map(signals)

    def sub(m):
        tok = m.group(0)
        if tok in _RESERVED:
            return tok
        full = amap.get(tok)
        if full is None:
            return tok          # 未映射的原子(表达式片段等)原样
        return rep_of(full)

    return re.sub(r'\s+', '', _ATOM_RE.sub(sub, formula))


def alias_reps(signals: Optional[Dict]) -> Dict[str, str]:
    """{别名: 等价类代表名}——跨模块重声明的网络身份校验用。"""
    out = {}
    for alias, s in (signals or {}).items():
        port = s.get('port')
        if not port or port.startswith('expr:'):
            continue
        m = s.get('module')
        pre = _inst_of_module(m) if m else None
        full = (pre + '_' + port.replace('.', '_')) if pre \
            else port.replace('.', '_')
        out[alias] = rep_of(full)
    return out


def sig_set_L2(signals: Optional[Dict]) -> frozenset:
    """{别名: {module, port}} → 等价类代表的集合(与 norm_L2 同映射)。"""
    amap = _alias_map(signals)
    return frozenset(rep_of(v) for v in amap.values())


def key_L3(formula: str, signals: Optional[Dict]) -> str:
    """因果对抽象(不保语义): 仅 neg_kb 与缓存键可用。"""
    try:
        from causal_pairs import causal_pairs
        amap = _alias_map(signals)
        cps = causal_pairs(formula)
        ks = tuple(sorted(tuple(sorted(rep_of(amap.get(a, a))
                                       for a in p)) for p in cps))
        atoms = sorted(a for a in _ATOM_RE.findall(formula)
                       if a not in _RESERVED and a not in amap)
        # 信号等价类代表集必须入键: 单信号公式因果对为空、别名又被从
        # atoms 排除, 不补则一切单信号公式共享 'L3|()|' 互相误并
        # (run_20260928 DFS 测试实证: G(req) 证伪误杀 G(rdy) 假设)
        sigs = tuple(sorted(set(rep_of(v) for v in amap.values())))
        return 'L3|{}|{}|{}'.format(repr(ks), '|'.join(atoms),
                                    '|'.join(sigs))
    except Exception:
        return 'L1|' + re.sub(r'\s+', '', formula)
