#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""proof_state: AGVerify 全局数据结构（DESIGN.md §3 + KB 复用规则）

三件套 + KB/反KB + 任务栈:
  nodes       扁平字典 id -> Node（树形靠节点内指针表达）
  registry    SignalRegistry（wire_id 归一的信号账本）
  kb          定理库（仅升级为 IC3_PROVEN 时写入; deps 恒空 → 无条件定理）
  neg_kb      反 KB（VIOLATED 的签名索引, 跨子任务可见, 任务开场查）
  failures    失败账本（只追加, 带 outcome: VIOLATED/TIMEOUT/ITER_EXCEED）
  stack       DFS 任务栈（assume 兑现子任务压栈; 失败时 unwind + 负短路）

已确认约定:
  - kind: "assert" | "assume"
  - MOD_PROVEN: 模块级条件已证(assume 未兑现); 兑现完成才升级 IC3_PROVEN
    并写 KB —— KB 恒为无条件定理, 不需要作废级联
  - 非 VIOLATED 结局隐含 BMC 已通过
  - 兑现节点 locked_conjunct; 循环防护 = 栈上未清偿 assume 签名检查
    + discharge 链深度预算 + 全局轮数熔断
"""

import json
import re
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from classify_prop import (ClassifyError, DesignReader, Hierarchy,
                           _port_on_side, classify)

# ---------------------------------------------------------------------------
# 外部可调参数（AGVerify/config.json, 不存在则用默认值）
# ---------------------------------------------------------------------------

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.json"
_DEFAULTS = {"rollback_max_fail": 20, "max_depth": 10,
             "max_rounds": 10, "max_agent_calls": 20}


def load_config() -> Dict:
    cfg = dict(_DEFAULTS)
    if CONFIG_PATH.exists():
        cfg.update(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
    return cfg


CONFIG = load_config()

# ---------------------------------------------------------------------------
# 状态机
# ---------------------------------------------------------------------------

PENDING = "PENDING"
BMC_FILTERED = "BMC_FILTERED"
MOD_PROVEN = "MOD_PROVEN"            # 模块级条件已证, 等 assume 兑现
BMC_FAILED = "BMC_FAILED"
IC3_FAILED = "IC3_FAILED"
IC3_PROVEN = "IC3_PROVEN"            # 终态: 条件全部兑现, 写 KB
TIMEOUT_UNPROVED = "TIMEOUT_UNPROVED"
SKIPPED = "SKIPPED"                   # 分解尝试超限, 跳过(不进有效性前提)

TRANSITIONS = {
    PENDING: {BMC_FILTERED, BMC_FAILED, IC3_FAILED, IC3_PROVEN,
              MOD_PROVEN, SKIPPED, TIMEOUT_UNPROVED},
    # PENDING→IC3_PROVEN: KB 复用; PENDING→MOD_PROVEN: 蕴含先行通过
    # BMC_FILTERED→PENDING: 多落点快速验证失败, 该性质重入队递归分解
    BMC_FILTERED: {MOD_PROVEN, IC3_PROVEN, IC3_FAILED, TIMEOUT_UNPROVED,
                   PENDING},
    MOD_PROVEN: {IC3_PROVEN, PENDING},        # 升级 / 回滚
    BMC_FAILED: set(),               # 全局证伪=终态: 假性质不可再分解
    IC3_FAILED: {PENDING},
    IC3_PROVEN: {IC3_PROVEN},          # 幂等(多落点/提升可能重复标记)
    TIMEOUT_UNPROVED: set(),
    SKIPPED: set(),
}
MAX_DEPTH = CONFIG["max_depth"]               # 分解深度(树深度制, 子=父+1)
TIMEOUT_RETRY_MAX = CONFIG.get("timeout_retry_max", 2)   # 等价性质超时重试上限
ROLLBACK_BASE = CONFIG["rollback_max_fail"]     # 根层级回滚预算

def _rollback_allowed(depth: int) -> int:
    """层级递减回滚预算: 根20次, 每深一层减半
    depth=0:20, depth=1:10, depth=2:7, depth=3:5, ..."""
    return max(1, math.ceil(ROLLBACK_BASE / (depth + 1)))


@dataclass
class Node:
    id: str
    kind: str                        # "assert" | "assume"
    formula: str
    nl: str = ""
    signals: Dict = field(default_factory=dict)
    derived: Dict = field(default_factory=dict)
    strategy: Optional[str] = None   # "CONJUNCT" | "ASSUME"
    children: List[str] = field(default_factory=list)
    assumes: List[str] = field(default_factory=list)
    discharged_by: Optional[str] = None   # assume 节点 → 兑现节点
    locked_conjunct: bool = False
    depth: int = 0                   # discharge 链深度（循环防护）
    status: str = PENDING
    fail_count: int = 0
    reuse_from: Optional[str] = None     # 复用命中的 KB 条目 id
    parent: Optional[str] = None
    assert_kind: str = "global"          # global: 断言语义 G p; once: 初始一次
    proven_at: Optional[str] = None      # 多落点验证实际证毕的模块
    pending_subs: int = 0                # 本轮分解中未决子任务数(批处理用)

    def subtree_ids(self, nodes: Dict) -> List[str]:
        out, stack = [], [self.id]
        while stack:
            cur = stack.pop()
            out.append(cur)
            n = nodes[cur]
            stack.extend(n.children)
            stack.extend(n.assumes)
            if n.discharged_by:
                stack.append(n.discharged_by)
        return out


# ---------------------------------------------------------------------------
# SignalRegistry（wire_id 归一）
# ---------------------------------------------------------------------------

def wire_id_of(signal: Dict, h: Hierarchy) -> str:
    """信号 -> 物理线 id。连接侧前缀命中 → conn:（含字段后缀）; 否则 sig:"""
    mod, port = signal["module"], signal["port"]
    for c in h.connections:
        a_mod, a_port = c.frm.split(".", 1)
        b_mod, b_port = c.to.split(".", 1)
        ends = sorted([f"{a_mod}.{a_port}", f"{b_mod}.{b_port}"])
        base = f"conn:{ends[0]}<->{ends[1]}"
        if a_mod == mod:
            suffix = _port_on_side(a_port, port)
            if suffix is not None:
                return base + suffix
        if b_mod == mod:
            suffix = _port_on_side(b_port, port)
            if suffix is not None:
                return base + suffix
    return f"sig:{mod}.{port}"


@dataclass
class WireEntry:
    views: Set[str] = field(default_factory=set)
    referenced_by: List[Tuple[str, str]] = field(default_factory=list)
    writer: Optional[str] = None
    readers: Set[str] = field(default_factory=set)


class SignalRegistry:
    def __init__(self, hierarchy: Hierarchy, reader: DesignReader):
        self.h = hierarchy
        self.reader = reader
        self.entries: Dict[str, WireEntry] = {}

    def register(self, node_id: str, signals: Dict) -> List[str]:
        wids = []
        for local, s in signals.items():
            wid = wire_id_of(s, self.h)
            if wid not in self.entries:
                self.entries[wid] = WireEntry()
                self._init_directions(wid)
            e = self.entries[wid]
            e.views.add(f'{s["module"]}.{s["port"]}')
            e.referenced_by.append((node_id, local))
            if wid not in wids:
                wids.append(wid)
        return wids

    def _init_directions(self, wid: str):
        e = self.entries[wid]
        m = re.match(r"conn:(\w+)\.([\w.]+)<->(\w+)\.([\w.]+)", wid)
        if not m:
            mm = re.match(r"sig:(\w+)\.", wid)
            if mm:
                e.writer = mm.group(1)
            return
        a_mod, a_port, b_mod, b_port = m.groups()
        da = self.reader.port_direction(a_mod, a_port)
        db = self.reader.port_direction(b_mod, b_port)
        if da == "Output":
            e.writer, e.readers = a_mod, {b_mod}
        elif db == "Output":
            e.writer, e.readers = b_mod, {a_mod}

    def unregister(self, node_id: str):
        dead = []
        for wid, e in self.entries.items():
            e.referenced_by = [r for r in e.referenced_by if r[0] != node_id]
            if not e.referenced_by:
                dead.append(wid)
        for wid in dead:
            del self.entries[wid]

    def wire_ids_of(self, node_id: str) -> List[str]:
        return [wid for wid, e in self.entries.items()
                if any(r[0] == node_id for r in e.referenced_by)]


# ---------------------------------------------------------------------------
# 签名工具
# ---------------------------------------------------------------------------

def norm_formula(f: str) -> str:
    return re.sub(r"\s+", "", f)


try:
    import sig_equiv as _se          # 信号等价类规范化服务(tools/)
except Exception:
    _se = None


def signature(formula: str, wire_ids: List[str],
              signals: Dict = None, level: int = 1) -> tuple:
    """KB/NegKB 匹配签名。档位契约:
    level=2 → 信号等价类规范化(保语义, KB 复用允许);
    level=3 → 因果对抽象(不保语义, 仅 NegKB);
    level=1 → 语法归一(降级)。"""
    if _se is not None and signals and level >= 2:
        if level == 2:
            return ('L2', tuple(sorted(_se.sig_set_L2(signals))),
                    _se.norm_L2(formula, signals))
        return ('L3', _se.key_L3(formula, signals))
    return ('L1', tuple(sorted(set(wire_ids))), norm_formula(formula))


# ---------------------------------------------------------------------------
# KB（正面定理） / NegKB（反例索引）
# ---------------------------------------------------------------------------

@dataclass
class KBEntry:
    kid: str
    formula: str                       # 规范化(签名/去重用)
    nl: str = ""
    formula_raw: str = ""             # 原始串(带空格, 可执行/回喂前提)
    wire_ids: List[str] = field(default_factory=list)
    node_origin: str = ""
    signals: Dict = field(default_factory=dict)   # 重建空设计声明用
    proven_at: Optional[str] = None               # 实际证毕的模块(多落点)

    @property
    def sig(self) -> Tuple[frozenset, str]:
        return signature(self.formula, self.wire_ids)


class KB:
    def __init__(self):
        self.entries: List[KBEntry] = []
        self._n = 0

    def add(self, formula: str, wire_ids: List[str], node_origin: str,
            nl: str = "", signals: Optional[Dict] = None,
            proven_at: Optional[str] = None,
            level: int = 1) -> KBEntry:
        self._n += 1
        e = KBEntry(f"T{self._n}", norm_formula(formula), nl,
                    wire_ids=list(wire_ids), node_origin=node_origin,
                    signals=signals or {}, proven_at=proven_at,
                    formula_raw=formula)
        e.sig_key = signature(formula, wire_ids, signals, level)
        self.entries.append(e)
        return e

    def lookup(self, formula: str, wire_ids: List[str],
               signals: Dict = None, level: int = 1) -> Optional[KBEntry]:
        sig = signature(formula, wire_ids, signals, level)
        return next((e for e in self.entries
                     if getattr(e, 'sig_key', None) == sig
                     or e.sig == sig), None)

    def summary(self) -> List[Dict]:
        """decomposer 提示层: 可用定理摘要(formula 为可执行原始串)"""
        return [{"id": e.kid, "formula": e.formula_raw or e.formula,
                 "nl": e.nl,
                 "wires": e.wire_ids,
                 **({"proven_at": e.proven_at} if e.proven_at else {})}
                for e in self.entries]


# ---------------------------------------------------------------------------
# 候选池（BFS 模式）: 全局BMC通过但快检未证毕的性质, run 内跨轮持久
# ---------------------------------------------------------------------------

# 候选池 (Candidate/CandidatePool) 已随机制移除 (2026-10-08 用户裁定)

@dataclass
class NegEntry:
    formula: str
    wire_ids: List[str] = field(default_factory=list)
    outcome: str = "VIOLATED"          # VIOLATED（确定性）| TIMEOUT（提示性）
    node_origin: str = ""
    round: int = 0


class NegKB:
    """反 KB: 已证伪结论的签名索引。VIOLATED 命中 → 任务开场直接失败短路。"""

    def __init__(self):
        self.entries: List[NegEntry] = []

    def add(self, formula: str, wire_ids: List[str], outcome: str,
            node_origin: str = "", round: int = 0,
            signals: Dict = None, level: int = 1):
        sig = signature(formula, wire_ids, signals, level)
        # 同签名保留最新结局
        self.entries = [e for e in self.entries
                        if getattr(e, 'sig_key',
                                   signature(e.formula, e.wire_ids)) != sig]
        e = NegEntry(norm_formula(formula), list(wire_ids),
                     outcome, node_origin, round)
        e.sig_key = sig
        self.entries.append(e)

    def lookup(self, formula: str, wire_ids: List[str],
               signals: Dict = None, level: int = 1) -> Optional[NegEntry]:
        sig = signature(formula, wire_ids, signals, level)
        return next((e for e in self.entries if e.outcome == "VIOLATED"
                     and getattr(e, 'sig_key',
                                 signature(e.formula, e.wire_ids)) == sig),
                    None)

    def summary(self) -> List[Dict]:
        return [{"formula": e.formula, "outcome": e.outcome,
                 "origin": e.node_origin} for e in self.entries]


# ---------------------------------------------------------------------------
# ProofState
# ---------------------------------------------------------------------------

class ProofStateError(Exception):
    pass


@dataclass
class FailRecord:
    round: int
    node: str
    kind: str
    outcome: str               # VIOLATED | TIMEOUT | ITER_EXCEED | MODULE_STUCK
    cause: str = ""
    evidence: str = ""
    hint: str = ""


class ProofState:
    def __init__(self, hierarchy: Hierarchy, reader: DesignReader,
                 root_prop: Dict):
        # 分解尝试双计数器(按签名): total 仅统计; current 重遇重置, 超限 SKIP
        self.attempts: Dict[Tuple, Dict[str, int]] = {}
        self.h = hierarchy
        self.reader = reader
        self.nodes: Dict[str, Node] = {}
        self.registry = SignalRegistry(hierarchy, reader)
        self.kb = KB()
        self.neg_kb = NegKB()
        # 公式级信号绑定登记(网络漂移检测)
        self._formula_nets = {}
        self.failures: List[FailRecord] = []
        # 等价性质(同 L2 签名)的超时尝试计数: TIMEOUT 不证伪, 允许在其它
        # 分解中再尝试, 但达上限后不再重跑(2026-09-28 用户语义)
        self.timeout_attempts: Dict[str, int] = {}
        self.round = 0
        self.stack: List[str] = []          # DFS 任务栈（节点 id）

        self._n = 0
        self.root = self.add_property(None, root_prop)["id"]
        self.stack.append(self.root)

    # ---------------- 节点构建 ----------------

    def _new_id(self) -> str:
        self._n += 1
        return f"N{self._n}"

    @staticmethod
    def _autocorrect_module(spec: Dict):
        """agent 指错模块时不拒绝, 直接改为信号实际归属(仅 atomic 情形)。
        children 的 module 与 assume 的 target_module 统一处理。"""
        sigs = spec.get("signals") or {}
        if not sigs:
            return
        mods = {s.get("module") for s in sigs.values()}
        if len(mods) != 1:
            return                      # 多模块/空: 交 classify
        actual = next(iter(mods))
        if spec.get("module") and spec["module"] != actual:
            spec["module"] = actual     # 纠偏(children 归属)
        if spec.get("target_module") and spec["target_module"] != actual:
            spec["target_module"] = actual   # 纠偏(assume 落点)

    @staticmethod
    def _normalize_signals(spec: Dict):
        """expr 信号补 port 占位（'expr:<表达式>'），统一后续处理"""
        for s in (spec.get("signals") or {}).values():
            if not s.get("port"):
                s["port"] = "expr:" + s.get("expr", "?")

    def _check_signal_hosts(self, spec: Dict):
        """入队前宿主校验: signal.module 的端口组前缀须在该模块端口表中。
        本地 0 成本拦截宿主写错（否则 40s sbt 编译才暴露）。"""
        for local, s in (spec.get("signals") or {}).items():
            mod, port = s["module"], s.get("port")
            if port is None or port.startswith("expr:"):
                # expr 内部状态校验 (2026-10-08): 引用非 io.* 的标识符
                # = 内部状态引用, 跨模块改写必败, 当场拒绝
                expr = s.get("expr") or ""
                if expr:
                    # 先剥掉所有 io.* 路径, 剩余标识符 = 内部信号
                    stripped = re.sub(r"io\.[A-Za-z0-9_.]+", "", expr)
                    ids = set(re.findall(
                        r"[a-z_][A-Za-z0-9_]*", stripped))
                    ids -= {"true", "false", "and", "or", "not",
                            "b", "h"}
                    bad = [x for x in ids
                           if not x[0].isupper()]  # 大写=类型/常量名
                    if bad:
                        raise ProofStateError(
                            f"expr 信号 {local} 引用了非端口信号 {bad}——"
                            f"内部状态在其他模块不可见, 跨模块改写必败; "
                            f"请改写为 io.* 端口信号的组合 (expr: {expr[:60]})")
                continue
            info = self.h.modules.get(mod)
            if info is None or not info.src:
                continue            # 未定义/无源码模块交 classify 处理
            if hasattr(self.reader, "port_path_exists") \
                    and not self.reader.port_path_exists(mod, port):
                ports = self.reader.ports(mod) if hasattr(
                    self.reader, "ports") else {}
                # 近似匹配纠正 (2026-10-06): 编辑距离<=2 的唯一候选 → 改写
                cand = self._fuzzy_port(port, ports)
                if cand:
                    spec["signals"][local]["port"] = cand
                    continue
                known = ", ".join(sorted(ports)) or "未知"
                raise ProofStateError(
                    f"信号 {local} 的路径 {mod}.{port} 不存在"
                    f"（{mod} 的端口: {known}; 已试近似匹配无唯一候选）"
                    f"——宿主模块或端口写错")

    @staticmethod
    def _fuzzy_port(port: str, ports) -> Optional[str]:
        """端口名近似匹配: 前缀树公共祖先下的编辑距离<=2 候选;
        唯一命中才纠正(多候选不猜)。端口路径含子包用最长后缀匹配。"""
        import difflib
        if not ports:
            return None
        keys = list(ports)
        scored = sorted(
            ((difflib.SequenceMatcher(None, port, k).ratio(), k)
             for k in keys), reverse=True)[:2]
        if len(scored) == 1 and scored[0][0] >= 0.85:
            return scored[0][1]
        if len(scored) == 2 and scored[0][0] >= 0.85 \
                and scored[0][0] - scored[1][0] >= 0.05:
            return scored[0][1]           # 显著最优才纠正
        # 前缀式: io.cpu.req.val 之于 io.cpu.req.valid (子字段漏写)
        pre = [k for k in keys if k.startswith(port) or port.startswith(k)]
        pre = [k for k in pre if abs(len(k) - len(port)) <= 8]
        if len(pre) == 1:
            return pre[0]
        return None

    def _build(self, node_id, spec: Dict, kind: str,
               locked: bool = False, depth: int = 0) -> Node:
        try:
            self._check_signal_hosts(spec)
            classified = classify(spec, self.h, self.reader)
        except ClassifyError as e:
            raise ProofStateError(str(e))
        node = Node(id=node_id, kind=kind, formula=spec["formula"],
                    nl=spec.get("nl", ""), signals=spec.get("signals", {}),
                    derived=classified["derived"], locked_conjunct=locked,
                    depth=depth,
                    assert_kind=spec.get("assert_kind", "global"))
        self.nodes[node_id] = node
        self.registry.register(node_id, classified["derived"].get("signals", {}))
        return node

    def check_binding_drift(self, formula: str, signals: Dict) -> None:
        """同名公式内信号绑定的网络身份漂移检测:
        同一公式(语法归一)再次出现时, 各别名的等价类代表必须一致——
        否则属【跨模块重声明偷换网络】(如 nastiReadReqReady 从授权侧
        io.icache.ar.ready 漂到外部侧 io.nasti.ar.ready), 拒绝。
        多落点改写(等价网重命名)的 rep 相同, 不受影响。"""
        if _se is None or not signals:
            return
        key = norm_formula(formula)
        cur = _se.alias_reps(signals)
        prev = self._formula_nets.get(key)
        if prev is None:
            self._formula_nets[key] = cur
            return
        for alias, rep in cur.items():
            old_rep = prev.get(alias)
            if old_rep is not None and old_rep != rep:
                raise ProofStateError(
                    f"信号 {alias} 的绑定发生网络漂移: 该公式此前绑定"
                    f" {old_rep}(等价类代表), 本次绑到 {rep}——同名端口"
                    f"在不同模块是不同网络。请使用等价端口(原网络在"
                    f"驱动模块侧的对应端口)或以新别名表述不同性质")

    def add_property(self, parent: Optional[str], spec: Dict,
                     depth: Optional[int] = None) -> Dict:
        """assert 节点入树。任务开场正负双查（复用/短路）。"""
        self._normalize_signals(spec)
        self.check_binding_drift(spec["formula"], spec.get("signals") or {})
        wids_probe = [wire_id_of(s, self.h)
                      for s in (spec.get("signals") or {}).values()]
        # 负 KB 短路: 同签名已 VIOLATED → 直接失败节点, 不重跑
        neg = self.neg_kb.lookup(spec["formula"], wids_probe,
                                 signals=spec.get("signals"), level=3)
        if neg is not None:
            node_id = self._new_id()
            neg_depth = depth if depth is not None else (
                self.nodes[parent].depth + 1 if parent else 0)
            node = Node(id=node_id, kind="assert", formula=spec["formula"],
                        nl=spec.get("nl", ""), signals=spec.get("signals", {}),
                        derived={"scope": "short-circuited"},
                        status=BMC_FAILED, depth=neg_depth,
                        reuse_from=None)
            self.nodes[node_id] = node
            if parent:
                node.parent = parent
                self.nodes[parent].children.append(node_id)
            self.record_failure(node_id, "VIOLATED", cause="NEG_KB_HIT",
                                evidence=f"先前在 {neg.node_origin} 已违反")
            return {"id": node_id, "reused_from": None,
                    "short_circuited": True}

        if depth is None:
            depth = self.nodes[parent].depth + 1 if parent else 0
        # ── 祖先重复检查(无环性, 2026-09-28 用户语义) ──
        # 进树时查祖先链是否有同签名性质: 命中 = 自我回归分解(祖先正在
        # 被分解又提出自己), 拒绝。非祖先的重复无关(合法的多次尝试证明,
        # 由 KB 复用/超时上限管辖)。KB 已证的同式例外(直接复用, 无回归)。
        if parent:
            kb_hit_early = self.kb.lookup(spec["formula"], wids_probe,
                                          signals=spec.get("signals"),
                                          level=2)
            if kb_hit_early is None:
                sig = signature(spec["formula"], wids_probe)
                anc = self.nodes[parent]
                while anc is not None:
                    try:
                        anc_sig = signature(
                            anc.formula, self.registry.wire_ids_of(anc.id))
                    except Exception:
                        anc_sig = None
                    if anc_sig == sig:
                        raise ProofStateError(
                            f"祖先重复: 与祖先 {anc.id} 同签名 "
                            f"({anc.formula[:50]}), "
                            f"禁止自我回归分解(该性质正处于分解链上, "
                            f"请提出不同形状的子性质或复用先验/KB)")
                    anc = self.nodes.get(anc.parent) if anc.parent else None
        # 超时重试上限短路: 等价性质(同签名)已 TIMEOUT 达上限 → 不再尝试
        if self.timeout_attempts.get(
                signature(spec["formula"], wids_probe), 0) >= TIMEOUT_RETRY_MAX:
            node_id = self._new_id()
            node = Node(id=node_id, kind="assert", formula=spec["formula"],
                        nl=spec.get("nl", ""), signals=spec.get("signals", {}),
                        derived={"scope": "timeout-bound"},
                        status=TIMEOUT_UNPROVED, depth=depth)
            self.nodes[node_id] = node
            if parent:
                node.parent = parent
                self.nodes[parent].children.append(node_id)
            self.record_failure(node_id, "TIMEOUT",
                                cause="TIMEOUT_RETRY_EXCEEDED",
                                evidence=f"等价性质超时 {TIMEOUT_RETRY_MAX} 次,"
                                         f"不再尝试(换模块/换形状也计同签名)")
            return {"id": node_id, "reused_from": None,
                    "short_circuited": True,
                    "short_circuit_reason": "timeout"}
        if parent and depth > MAX_DEPTH:
            raise ProofStateError(
                f"分解深度超限({MAX_DEPTH}): 层级耗尽, 请给出可直接证明"
                f"的性质或利用已证 assume")
        node_id = self._new_id()
        self._normalize_signals(spec)
        self._autocorrect_module(spec)
        node = self._build(node_id, spec, kind="assert", depth=depth)
        if parent:
            node.parent = parent
            self.nodes[parent].children.append(node_id)

        hit = self.kb.lookup(spec["formula"],
                             self.registry.wire_ids_of(node_id),
                             signals=spec.get("signals"), level=2)
        if hit is not None:
            node.status = IC3_PROVEN
            node.reuse_from = hit.kid
            return {"id": node_id, "reused_from": hit.kid,
                    "short_circuited": False}
        return {"id": node_id, "reused_from": None, "short_circuited": False}

    @staticmethod
    def _assume_gate_signals(formula: str) -> Dict:
        """assume 信号门禁的分域规则(2026-09-21 定):
        - 蕴含式: 后件信号须为 Input; 前件(停滞条件)允许任意方向
          (停滞公平 (G !目标输出) -> FG 环境输入 的前件引用输出是本质)
        - 单原子信号性质(F x / G x): 该信号须为 Input
        - 其它非蕴含形态(U/&/G(a&b)等): 允许任意方向
        返回 {信号名: 'must_input' | 'any'}; 解析失败保守 must_input。
        """
        import re as _re
        atoms = set(a for a in _re.findall(r'[A-Za-z_]\w*', formula)
                    if a not in ('G', 'F', 'X', 'U', 'FG', 'GF', 'and', 'or',
                                 'not', 'true', 'false'))
        # 顶层蕴含拆分(括号外第一个 ->)
        depth, antecedent, cons_start = 0, None, None
        i = 0
        while i < len(formula) - 1:
            c = formula[i]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
            elif depth == 0 and formula[i:i + 2] == '->' \
                    and antecedent is None:
                antecedent = formula[:i]
                cons_start = i + 2
            i += 1
        if antecedent is not None:
            cons = formula[cons_start:]
            cons_atoms = set(a for a in _re.findall(r'[A-Za-z_]\w*',
                                                     cons)
                             if a not in ('G', 'F', 'X', 'U', 'FG', 'GF', 'and',
                                          'or', 'not', 'true', 'false'))
            return {a: ('must_input' if a in cons_atoms else 'any')
                    for a in atoms}
        if len(atoms) == 1:
            return {a: 'must_input' for a in atoms}
        return {a: 'any' for a in atoms}

    def add_assume(self, target_node_id: str, spec: Dict) -> str:
        """assume 节点入树（decomposer 的 ASSUME 决策落地）。

        门禁:
          0. 禁止 assume 嵌套（目标节点已是 assume → 拒绝）
          1. 输入侧检查（分域: 蕴含后件/单信号性质须为 Input;
             蕴含前件及其它形态允许任意方向）
          2. 循环防护: 签名不得命中【栈上祖先的未清偿 assume】
          3. 深度预算: discharge 链深度上限
        副作用: 自动挂兑现节点并压栈。
        """
        target = self.nodes[target_node_id]
        if target.kind == "assume" or target.locked_conjunct:
            raise ProofStateError(
                f"禁止 assume 嵌套: 目标节点 {target_node_id} "
                f"{'是 assume' if target.kind == 'assume' else '是兑现节点(locked)'}"
                f"（assume 约束模块输入, 不能通过再加约束来证明——"
                f"应改释为驱动模块上的子性质分解）")
        self._normalize_signals(spec)
        self._autocorrect_module(spec)
        self._check_signal_hosts(spec)
        self.check_binding_drift(spec["formula"], spec.get("signals") or {})
        gate = self._assume_gate_signals(spec["formula"])
        for local, s in (spec.get("signals") or {}).items():
            if gate.get(local, 'must_input') != 'must_input':
                continue          # 前件/非蕴含: 任意方向允许
            d = self.reader.port_direction(s["module"], s["port"])
            if d == "Output":
                raise ProofStateError(
                    f"assume 信号 {local}({s['module']}.{s['port']}) 位于"
                    f"公式的后件/单信号位置, 在目标侧为 Output——"
                    f"assume 书写错误(约束模块自身输出的应改为子性质)")

        wids = [wire_id_of(s, self.h) for s in (spec.get("signals") or {}).values()]
        cyc = self._find_pending_obligation(spec["formula"], wids)
        if cyc is not None:
            raise ProofStateError(
                f"循环依赖: 该 assume 与栈上未清偿的 assume {cyc} 签名相同"
                f"（还债过程中又借了同样的债）, 拒绝该分解决策")

        new_depth = target.depth + 1
        if new_depth > MAX_DEPTH:
            raise ProofStateError(
                f"分解深度超限({MAX_DEPTH}): assume 层级耗尽, 请给出可直接"
                f"证明的性质或利用已证 assume")
        aid = self._new_id()
        self.nodes[aid] = Node(id=aid, kind="assume", formula=spec["formula"],
                               nl=spec.get("nl", ""),
                               signals=spec.get("signals", {}),
                               derived={"scope": "assume"},
                               depth=new_depth, parent=target_node_id,
                               assert_kind=spec.get("assert_kind", "global"))
        target.assumes.append(aid)
        self._create_discharge(aid)
        return aid

    def _attempt_key(self, node) -> Tuple:
        wids = self.registry.wire_ids_of(node.id)
        return signature(node.formula, wids)

    def register_attempt(self, node_id) -> bool:
        """节点进入一次分解尝试。返回 False 表示当前尝试已超限(应 SKIP)。"""
        node = self.nodes[node_id]
        k = self._attempt_key(node)
        rec = self.attempts.setdefault(k, {"total": 0, "current": 0})
        rec["total"] += 1
        rec["current"] += 1
        return rec["current"] <= _rollback_allowed(node.depth)

    def refund_attempt(self, node_id):
        """退还一次尝试计数: 编译错误轮可能是 RTL 压缩问题而非分解
        质量问题, 不占该节点额度(仅减 current, total 保留审计)。"""
        node = self.nodes.get(node_id)
        if not node:
            return
        k = self._attempt_key(node)
        rec = self.attempts.get(k)
        if rec and rec["current"] > 0:
            rec["current"] -= 1

    def reset_attempt(self, node_id):
        """签名重遇(复用命中/重新入树)时重置当前计数"""
        node = self.nodes.get(node_id)
        if node:
            k = self._attempt_key(node)
            if k in self.attempts:
                self.attempts[k]["current"] = 0

    def _find_pending_obligation(self, formula: str,
                                 wire_ids: List[str]) -> Optional[str]:
        """栈上祖先的未清偿 assume 签名检查。命中返回节点 id。"""
        sig = signature(formula, wire_ids)
        # 沿栈自底向上收集所有节点, 取其 assume 中兑现未完成者
        for nid in self.stack:
            n = self.nodes.get(nid)
            if not n:
                continue
            for aid in n.assumes:
                a = self.nodes[aid]
                d = self.nodes.get(a.discharged_by or "")
                if d is not None and d.status == IC3_PROVEN:
                    continue          # 已清偿
                awids = [wire_id_of(s, self.h)
                         for s in (a.signals or {}).values()]
                if signature(a.formula, awids) == sig:
                    return aid
        return None

    def _create_discharge(self, assume_id: str) -> str:
        """兑现节点 = assume 改释为 assert。开场正负双查:
        KB 命中 → 直接 PROVEN; 反 KB 命中 → 直接失败短路。"""
        a = self.nodes[assume_id]
        wids = self.registry.register(assume_id, a.signals)
        did = self._new_id()
        # 兑现节点与 assume 共享信号注册（正负双查/失败入账都要用 wire 归属）
        d = Node(id=did, kind="assert", formula=a.formula, nl=a.nl,
                 signals=a.signals, derived={"scope": "discharge"},
                 strategy="CONJUNCT", locked_conjunct=True,
                 depth=a.depth + 1, parent=assume_id,
                 assert_kind=a.assert_kind)
        self.nodes[did] = d
        a.discharged_by = did
        # 兑现节点也注册信号引用（wire_ids_of(did) 需要命中）
        for local, s in (a.signals or {}).items():
            wid = wire_id_of(s, self.h)
            if wid in self.registry.entries:
                self.registry.entries[wid].referenced_by.append((did, local))

        hit = self.kb.lookup(a.formula, wids,
                             signals=a.signals, level=2)
        if hit is not None:
            d.status = IC3_PROVEN
            d.reuse_from = hit.kid
            return did
        neg = self.neg_kb.lookup(a.formula, wids,
                                 signals=a.signals, level=3)
        if neg is not None:
            d.status = BMC_FAILED
            self.record_failure(did, "VIOLATED", cause="NEG_KB_HIT",
                                evidence=f"先前在 {neg.node_origin} 已违反")
            return did
        # 超时重试上限短路: 等价性质已 TIMEOUT 达上限, 兑现不再尝试
        if self.timeout_attempts.get(signature(a.formula, wids), 0) \
                >= TIMEOUT_RETRY_MAX:
            d.status = TIMEOUT_UNPROVED
            d.derived["scope"] = "timeout-bound"
            self.record_failure(did, "TIMEOUT",
                                cause="TIMEOUT_RETRY_EXCEEDED",
                                evidence=f"等价性质超时 {TIMEOUT_RETRY_MAX} 次,"
                                         f"兑现不再尝试")
            return did
        self.stack.append(did)
        return did

    # ---------------- 状态与账本 ----------------

    def prune_stale_assumes(self, node_id: str,
                            keep_formulas: Optional[List[str]] = None) -> int:
        """清扫遗留 assume (2026-10-05 修复, N86 虚假闭合教训):
        假设的效力只属于提出它的那一轮。新一轮决策落地时, 凡不在本轮
        keep_formulas 里的旧假设(含其兑现子树)整体摘除——否则兑现失败的
        假设残留在 node.assumes, 后续模块验证 with_assumes=True 全量烘焙,
        未兑现的环境类假设会滤掉反例轨迹造成虚假证毕。
        已证毕的兑现节点删除无碍(定理在 KB, 复用可重挂)。返回摘除数。"""
        keep = {(f or "").replace(" ", "") for f in (keep_formulas or [])}
        node = self.nodes[node_id]
        doomed = []
        for aid in list(getattr(node, "assumes", None) or []):
            a = self.nodes.get(aid)
            if a is None:
                node.assumes.remove(aid)
                continue
            if a.formula.replace(" ", "") in keep:
                continue
            for sid in a.subtree_ids(self.nodes):
                doomed.append(sid)
            node.assumes.remove(aid)
        if doomed:
            ds = set(doomed)
            for sid in doomed:
                self.registry.unregister(sid)
                self.nodes.pop(sid, None)
            self.stack = [s for s in self.stack if s not in ds]
        return len(doomed)

    def mark(self, node_id: str, status: str):
        node = self.nodes[node_id]
        if status == node.status:
            return                      # 幂等: 重复标记同状态无害
        if status not in TRANSITIONS.get(node.status, set()):
            # 终态互改(SKIPPED/BMC_FAILED 等败者标记)视为败者保持, 不再升格
            if status in (SKIPPED, BMC_FAILED) and node.status in (SKIPPED, BMC_FAILED):
                return
            raise ProofStateError(
                f"非法状态迁移 {node_id}: {node.status} -> {status}")
        node.status = status
        if status == TIMEOUT_UNPROVED:
            # 等价性质超时计数(创建短路用)
            try:
                k = self._attempt_key(node)
                self.timeout_attempts[k] = self.timeout_attempts.get(k, 0) + 1
            except Exception:
                pass
        if status == IC3_PROVEN:
            self.try_kb_ingest(node_id)
            # 债清补录: 兑现节点证毕时, 其假设的挂靠目标若已是干净的
            # IC3_PROVEN(先前因本债未清被门禁拦下), 现在满足条件 → 补录
            if (node.kind == "assert"
                    and (node.derived or {}).get("scope") == "discharge"):
                a = self.nodes.get(node.parent)
                tgt = self.nodes.get(a.parent) if a else None
                if tgt is not None and tgt.status == IC3_PROVEN:
                    self.try_kb_ingest(tgt.id)

    def try_kb_ingest(self, node_id) -> bool:
        """入库门禁 (2026-10-06): 未清偿 assume 的证毕是【条件证毕】,
        不得入 KB——否则 N86 型污染(依赖幽灵假设)直通定理库。
        幂等: 已在 KB(按来源节点)则跳过。返回是否入库。"""
        node = self.nodes.get(node_id)
        if not node or node.status != IC3_PROVEN:
            return False
        for e in self.kb.entries:
            if e.node_origin == node_id:
                return False
        for aid in (getattr(node, "assumes", None) or []):
            a = self.nodes.get(aid)
            d = self.nodes.get(a.discharged_by) if a else None
            if d is None or d.status != IC3_PROVEN:
                return False
        self.kb.add(node.formula,
                    self.registry.wire_ids_of(node_id), node_id, node.nl,
                    signals=node.signals,
                    proven_at=getattr(node, "proven_at", None),
                    level=2)
        return True

    def record_failure(self, node_id: str, outcome: str, cause: str = "",
                       evidence: str = "", hint: str = "") -> str:
        node = self.nodes[node_id]
        node.fail_count += 1
        self.failures.append(FailRecord(
            self.round, node_id, node.kind, outcome, cause, evidence, hint))
        # VIOLATED → 反 KB（跨子任务可见的负面知识）
        # MODULE_STUCK(多落点快检全败, 全局BMC已通过)不是证伪, 不进反KB
        if outcome == "VIOLATED":
            self.neg_kb.add(node.formula,
                            self.registry.wire_ids_of(node_id),
                            "VIOLATED", node_id, self.round,
                            signals=node.signals, level=3)
        return ("global" if node.fail_count >= _rollback_allowed(node.depth)
                else "local")

    # ---------------- 回滚 ----------------

    def rollback(self, node_id: str, scope: str = "local"):
        """local: 删子树, 节点回 PENDING; global: 对父节点做 local。
        失败历史（failures / fail_count / neg_kb）保留。"""
        if scope == "global":
            parent = self.nodes[node_id].parent
            if parent is None:
                raise ProofStateError("根节点不可全局回滚")
            node_id = parent
        node = self.nodes[node_id]
        # 回滚=分解方案作废: 只删未决节点; PROVEN/TIMEOUT 终态节点保留
        # (定理已入KB, 保留树挂点供本轮有效性前提/终止判定/溯源使用;
        #  它们随 children 清空成为孤儿终态节点, 不阻塞 done/不影响复用)
        KEEP = (IC3_PROVEN, TIMEOUT_UNPROVED)
        doomed, kept = [], []
        for cid in list(node.children) + list(node.assumes):
            for sid in self.nodes[cid].subtree_ids(self.nodes):
                if self.nodes[sid].status in KEEP:
                    kept.append(sid)
                else:
                    doomed.append(sid)
        node.children, node.assumes = [], []
        node.strategy = None
        node.status = PENDING
        node.reuse_from = None
        node.pending_subs = 0
        # 保留节点脱离方案(父指针保留供溯源), 不删不注销
        for did in doomed:
            self.registry.unregister(did)
            self.nodes.pop(did, None)
        self.stack = [s for s in self.stack if s not in set(doomed)]
        return {"removed": doomed, "kept_proven": kept}

    # ---------------- 检查与终止 ----------------

    def check_cycles(self):
        """树边 DFS 检环（防御性: 树由追加构建, 结构上应无环）"""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {i: WHITE for i in self.nodes}

        def dfs(u):
            color[u] = GRAY
            n = self.nodes[u]
            for v in n.children + n.assumes + ([n.discharged_by]
                                                if n.discharged_by else []):
                if v not in self.nodes:
                    raise ProofStateError(f"{u} 指向缺失节点 {v}")
                if color[v] == GRAY:
                    raise ProofStateError(f"依赖环: {u} -> {v}")
                if color[v] == WHITE:
                    dfs(v)
            color[u] = BLACK

        for i in self.nodes:
            if color[i] == WHITE:
                dfs(i)

    def done(self) -> bool:
        if self.nodes[self.root].status != IC3_PROVEN:
            return False
        for n in self.nodes.values():
            if n.status in (BMC_FAILED, SKIPPED):
                continue                      # 筛掉/跳过: 非阻塞终态
            if n.kind == "assume":
                # assume 不是证明任务, 不查自身状态, 只查兑现。
                # 兑现必须真正 IC3_PROVEN——超时未证不算清偿
                # (假设可能错误或过难, 应反馈重迭代而非视为通过)
                d = self.nodes.get(n.discharged_by or "")
                if d is None or d.status != IC3_PROVEN:
                    return False
            elif n.status == PENDING:
                return False
        return True

    # ---------------- 持久化 ----------------

    def snapshot(self, path: str):
        obj = {
            "root": self.root, "round": self.round, "stack": self.stack,
            "nodes": {i: vars(n) for i, n in self.nodes.items()},
            "registry": {w: {"views": sorted(e.views),
                             "referenced_by": e.referenced_by,
                             "writer": e.writer,
                             "readers": sorted(e.readers)}
                         for w, e in self.registry.entries.items()},
            "kb": [vars(e) for e in self.kb.entries],
            "neg_kb": [vars(e) for e in self.neg_kb.entries],
            "failures": [vars(f) for f in self.failures],
        }
        Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2),
                              encoding="utf-8")
