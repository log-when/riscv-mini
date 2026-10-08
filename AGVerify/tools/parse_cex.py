#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""parse_cex: 反例 VCD → 结构化时序摘要（供 critic 阅读）

复用 AssertionGeration 的 Verilog_VCD 库（稳定解析器）。
VCD 信号名是展平端口名: io.cpu.req.valid → io_cpu_req_valid;
空设计槽位 io.s1 → io_s1。按 cha_verify signals(别名,路径,编号)
生成候选名匹配, 提取反例窗口(最后 K 个变化时刻)的取值表。
"""

from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple

from Verilog_VCD.Verilog_VCD import parse_vcd
from sys_parser import parse_sys_proper

LAST_K = 20         # 反例窗口: 最后 K 个变化时刻


def _flatten(path: str) -> str:
    return path.replace(".", "_")


def cex_timeline(vcd_path: str,
                 signals: List[tuple],
                 last_k: int = LAST_K) -> Optional[Dict]:
    """VCD + cha_verify signals → {cycle_<time>: {别名: 值}}。

    signals: [(别名, 路径, 编号)]；路径含实例前缀/io.sN 均可。
    找不到文件或匹配不到任何信号返回 None。
    """
    if not vcd_path or not Path(vcd_path).exists():
        return None
    data = parse_vcd(vcd_path)
    # 展平名 → (tv 列表, 位宽)
    by_name = {}
    for entry in data.values():
        tv = entry.get("tv") or []
        for net in entry.get("nets", []):
            by_name.setdefault(net["name"],
                               (tv, int(net.get("size", 1))))
    # 别名 → 展平名映射
    alias_map = {}
    for alias, path, _n in signals:
        cand = _flatten(path)
        if cand in by_name:
            alias_map[alias] = cand
    if not alias_map:
        return None
    # 汇总相关信号的全部变化时刻, 取最后 K 个
    times = sorted({t for a in alias_map
                    for t, _ in by_name[alias_map[a]][0]})
    window = times[-last_k:]
    out = {}
    for t in window:
        row = {}
        for alias, vcdn in alias_map.items():
            tv, width = by_name[vcdn]
            v = next((val for tt, val in reversed(tv) if tt <= t), None)
            if v is None:
                continue
            if width == 1:
                row[alias] = v
            else:
                # 宽向量: 二进制转十进制, x/z 保留原样
                row[alias] = str(int(v, 2)) if v.strip("01") == "" else v
        if row:
            out[f"cycle_{t}"] = row
    return out or None


def _fmt_val(v: str, width: int) -> str:
    """1-bit 原样; 宽向量转 0x 十六进制(x/z 保留)"""
    if width <= 1:
        return v
    return ("0x%x" % int(v, 2)) if v.strip("01xzXZ") == "" \
        and v.strip("01") == "" else v


# ---------------------------------------------------------------------------
# .sys 数据流图 → 敏感信号集(反例波形抽象)
# ---------------------------------------------------------------------------

_SYS_FUNC_WORDS = {
    "eq", "neq", "and", "or", "not", "ite", "concat", "implies",
    "add", "sub", "mul", "udiv", "urem",
    "ult", "ule", "ugt", "uge", "slt", "sle", "sgt", "sge",
    "shl", "shr", "sra", "srl", "sll", "xor", "xnor", "nand", "nor",
    "zext", "uext", "sext", "msb", "slice", "mux",
}
_SYS_CONST_RE = re.compile(r"\d+'\w[0-9a-fA-FxXzZ_]*")
_SYS_ID_RE = re.compile(r"[A-Za-z_]\w*")
_SYS_DEF_RE = re.compile(r"^(input|state|node|output|constraint|bad)\s+(\S+)")
_SYS_TRAN_RE = re.compile(r"^\[(init|next)\]\s+(.*)$")
# FIRRTL 展平中间线: <mod>__T_N / __GEN_N / port_T / 存储器端口线等
_INTERMEDIATE_RE = re.compile(
    r"_T$|__T(_\d+)?$|__GEN(_\d+)?$|_T_\d+$|_MPORT_|_rmeta_|rand_|dataMem_|metaMem_|tagMem_|^eq_")

def _sys_rhs_ids(expr: str) -> List[str]:
    """RHS 表达式里的信号标识符(剔除函数名/常量)"""
    e = _SYS_CONST_RE.sub(" ", expr)
    return [t for t in _SYS_ID_RE.findall(e)
            if t not in _SYS_FUNC_WORDS]


def parse_sys(sys_path: str) -> Tuple[Dict[str, set], Dict[str, set], set]:
    """.sys → (正向邻接, 反向邻接, 保留名集合)。
    覆盖 node/output/constraint/bad 定义行与 state 的 [init]/[next] 行。
    保留名集合 = input ∪ state——组合 node 全部是派生线, 输出时删除。"""
    fwd: Dict[str, set] = {}
    bwd: Dict[str, set] = {}
    keep: set = set()

    def add(a, b):
        fwd.setdefault(a, set()).add(b)
        bwd.setdefault(b, set()).add(a)

    cur_state = None
    for line in open(sys_path, encoding="utf-8", errors="ignore"):
        s = line.strip()
        if not s:
            continue
        m = _SYS_TRAN_RE.match(s)
        if m and cur_state:
            for i in _sys_rhs_ids(m.group(2)):
                add(i, cur_state)
            continue
        m = _SYS_DEF_RE.match(s)
        if not m:
            continue
        kind, name = m.groups()
        cur_state = name if kind == "state" else None
        if kind in ("input", "state"):
            keep.add(name)
            continue
        if "=" in s:
            for i in _sys_rhs_ids(s.split("=", 1)[1]):
                add(i, name)
    return fwd, bwd, keep


def find_simple_cycles(sys_path: str, seeds: List[str],
                       max_len: int = 8,
                       named_only: bool = True,
                       max_cycles: int = 200,
                       strict: bool = False) -> List[List[str]]:
    """经过种子信号的【简单环】挖掘。

    在原始数据流图上 DFS 搜索简单环(中间节点不重复), 输出时把
    组合链压缩为 keep(input/state)+种子 的序列——语义清晰。

    max_len: 原始图路径长度上限(防爆炸)。
    strict=True: 折叠环必须在原始图上可展开为真正的简单环——每条
    折叠边展开为具体路径, 所有中间点不得经过环内任何成员(含同族
    存储单元的具体 cell), 否则丢弃该环。
    返回: [[keep_sig1, keep_sig2, ..., keep_sig1] ...] 按长度升序。
    """
    if strict:
        raw_fwd, _, raw_keep = parse_sys_proper(sys_path, fold=False)
    else:
        raw_fwd = None
    fwd, bwd, keep = parse_sys_proper(sys_path)
    seed_set = {s for s in seeds if s in fwd or s in bwd}
    if not seed_set:
        return []
    # 过滤 rand 系建模节点(存储器随机初始化选择位)——它们制造伪反馈环
    keep = {k for k in keep if 'rand' not in k and 'invalid' not in k
            and 'disabled' not in k}
    keep_or_seed = keep | seed_set

    # 折叠名 → 同族具体单元集合(含自身)
    import re as _re
    family = {}
    if raw_fwd is not None:
        all_raw = set(list(raw_fwd.keys()))
        for n in keep_or_seed:
            m = _re.match(r'^(.*)\[\*\]$', n)
            if m:
                base = m.group(1)
                fam = {x for x in all_raw
                       if x.startswith(base + '_')
                       and x[len(base) + 1:].isdigit()}
                family[n] = fam if fam else {n}
            else:
                family[n] = {n}

    def _members(cycle):
        """环内全部成员的原始具体名集合"""
        out = set()
        for n in cycle:
            out |= family.get(n, {n})
        return out

    def _expand_edge(x, y, forbidden):
        """原始图上 x族→y族 的最短组合路径, 中间点避开 forbidden。
        (本边端点族 x/y 自身不在中间点禁用之列)
        返回 (起点具体名, 终点具体名, 中间点元组) 或 None。"""
        fx = family.get(x, {x})
        fy = family.get(y, {y})
        inter_forbidden = (forbidden - fx - fy) | fx | fy
        # 中间点不得经过任何端点族成员(含起点族其他 cell)
        starts = fx
        targets = fy
        from collections import deque as _dq
        q = _dq([(s, [s]) for s in starts])
        seen = set(starts)
        while q:
            cur, path = q.popleft()
            for z in raw_fwd.get(cur, ()):
                if z in targets:
                    return path[0], z, tuple(path[1:])
                if z not in seen and z not in inter_forbidden:
                    seen.add(z)
                    q.append((z, path + [z]))
        return None

    def _validate(cycle):
        """折叠环 → 原始图逐边展开, 全部成功且中间点互不重复才算过"""
        used = set()
        expansions = []
        for x, y in zip(cycle, cycle[1:]):
            r = _expand_edge(x, y, used | _members(cycle))
            if r is None:
                return None
            sx, ty, mids = r
            # 中间点登记为已用(具体名), 端点登记其折叠代表
            used |= set(mids)
            used |= family.get(x, {x}) if len(family.get(x, ())) > 1 else {sx}
            used |= family.get(y, {y}) if len(family.get(y, ())) > 1 else {ty}
            expansions.append((sx, ty, mids))
        return expansions

    def _fold_succ(x):
        """x 经纯组合链(不经过其他 keep)可达的 keep_or_seed 节点"""
        out = set()
        stack = [x]
        seen = {x}
        while stack:
            y = stack.pop()
            for z in fwd.get(y, ()):
                if z in keep_or_seed:
                    out.add(z)      # 到达 keep/种子, 记录不再展开
                elif z not in seen:
                    seen.add(z)
                    stack.append(z)  # 组合节点, 继续穿透
        return out

    # 构建折叠图: keep_or_seed 节点间的边(经组合链)
    folded: Dict[str, set] = {}
    for x in keep_or_seed:
        if x in fwd:
            folded[x] = _fold_succ(x)
    # 种子若不在 keep, 从种子出发也建边
    for s in seed_set:
        if s in fwd and s not in folded:
            folded[s] = _fold_succ(s)

    cycles: List[List[str]] = []
    seen_keys = set()
    # 枚举上限: strict 模式下 max_cycles 是"验证通过收集数",
    # 枚举本身用一个更大的固定池
    MAX_CYCLES = max(max_cycles, 200000) if strict else max_cycles

    for start in sorted(seed_set):
        if start not in folded:
            continue
        # DFS on folded graph
        def _dfs(cur, path, on_path):
            if len(cycles) >= MAX_CYCLES:
                return
            if len(path) > max_len:
                return
            for nxt in folded.get(cur, ()):
                if nxt == start:
                    # 闭环!
                    cyc = tuple(path)
                    if cyc not in seen_keys:
                        seen_keys.add(cyc)
                        cycles.append(list(path) + [start])
                    continue
                if nxt in on_path:
                    continue
                _dfs(nxt, path + [nxt], on_path | {nxt})

        _dfs(start, [start], {start})

    if strict:
        # 惰性验证: 折叠环按长度降序逐个在原始图上展开验证,
        # 收满 max_cycles 个严格环即停(避免对几十万候选全量 BFS)
        cycles.sort(key=len, reverse=True)
        verified: List[List[str]] = []
        for c in cycles:
            if len(verified) >= max_cycles:
                break
            if _validate(c):
                verified.append(c)
        verified.sort(key=len)
        return verified

    cycles.sort(key=len)
    return cycles


def sensitive_set(sys_path: str, seeds: List[str],
                  named_only: bool = True) -> List[str]:
    """种子集 A 的【路径敏感集】: 恰好落在 A 内某信号流向另一信号的
    通路上的节点(= 正向可达 ∩ 反向可达), 附带种子自身。
    悬挂侧枝/reset 等不在种子间通路上的信号不被捕捉。
    named_only=True: 剔除 FIRRTL 展平的中间线(_T_N/_GEN_N 等无语义名),
    只保留命名信号(io_*/state/寄存器名)——通路计算仍用全图,
    仅结果过滤(LLM 归因只需命名信号, 体积缩一个量级)。"""
    fwd, bwd, keep = parse_sys(sys_path)
    S = [s for s in seeds if s in fwd or s in bwd]
    F, stack = set(), list(S)
    while stack:
        x = stack.pop()
        for y in fwd.get(x, ()):
            if y not in F:
                F.add(y)
                stack.append(y)
    B, stack = set(), list(S)
    while stack:
        x = stack.pop()
        for y in bwd.get(x, ()):
            if y not in B:
                B.add(y)
                stack.append(y)
    res = (F & B) | set(S)
    if named_only:
        # 白名单式: 只保留 input/state(寄存器与自由输入)——
        # 组合 node 全部是派生线, 输出删除
        res = {s for s in res if s in keep}
    return sorted(res)


def cex_full_timeline(vcd_path: str,
                      last_k: int = LAST_K) -> Optional[Dict]:
    """VCD → 反例窗口【全部信号】取值表(不限性质相关信号)。

    {cycle_<time>: {vcd展平名: 值}}; 1-bit 为 0/1, 宽向量为 0x十六进制。
    只保留窗口内至少变化过一次的信号(过滤常量), 名字排序稳定。
    """
    if not vcd_path or not Path(vcd_path).exists():
        return None
    data = parse_vcd(vcd_path)
    by_name = {}
    for entry in data.values():
        tv = entry.get("tv") or []
        for net in entry.get("nets", []):
            by_name.setdefault(net["name"],
                               (tv, int(net.get("size", 1))))
    if not by_name:
        return None
    times = sorted({t for tv, _w in by_name.values() for t, _ in tv})
    if not times:
        return None
    window = times[-last_k:]
    t0 = window[0]
    # 全信号保留(含恒定不变的): 卡死态(如 state 恒为 sRead)正是关键
    # 诊断信息; 体积控制由下游敏感集白名单过滤负责
    names = sorted(by_name)
    out = {}
    for t in window:
        row = {}
        for n in names:
            tv, width = by_name[n]
            v = next((val for tt, val in reversed(tv) if tt <= t), None)
            if v is None:
                continue
            row[n] = _fmt_val(v, width)
        if row:
            out[f"cycle_{t}"] = row
    return out or None
