#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dispatcher: AGVerify 主循环（DESIGN.md §6, DFS 任务栈版）

驱动 proof_state 的任务栈:
  PENDING 节点  → decomposer 分解 → children/assume 兑现任务压栈
                  （新 child 先过全局 Tile BMC 筛选, FAIL 即分解失败）
  BMC_FILTERED  → 模块级 IC3（assume 作前提）
                  PASS + 无 assume → IC3_PROVEN（写 KB）
                  PASS + 有 assume → MOD_PROVEN（等兑现）
                  FAIL → critic → 回滚（局部/全局）
  兑现节点完成  → unwind 时向上提升 MOD_PROVEN 祖先
  轮数/回溯熔断  → max_rounds

用法:
  python dispatcher.py spec/hierarchy.json spec/properties.json
"""

import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agents"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import proof_state as ps
from classify_prop import ChiselFileReader, DesignReader, Hierarchy, rewrite_path, rewrite_expr
import cha_verify
import llm
from decomposer import DecomposeError, decompose


class SignalGenError(Exception):
    """信号条目缺少合法 port/expr, 生成的 Scala 必然编译失败。
    在物化前抛出, 转为可重试的 ERROR 判定而非污染 sbt 编译。"""


# 同网络退化永真式: 等价类归并后公式变为 A -> (X)F A (如 arbWriteRespValid
# 与 dcacheWriteRespValid 同一根线)。这类公式 BA 化简为空原子会让 hoaParser
# 抛 "BA is empty", 本应是平凡 PASS —— 在此短路。
_TAUT_SELF_F = re.compile(r"^(A\d+)\s*->\s*(?:(?:X\s*)?F\s*)?\1$")


def _trivially_true(formula: str, decls) -> bool:
    """decls: [(alias, port, num)]。同端口别名归一化为 A0/A1/... 后再匹配,
    覆盖跨别名同网络塌缩 (别名不同但 port 相同, PSL 映射后同为 pN)。"""
    f = formula.strip()
    if _TAUT_SELF_F.match(f):
        return True
    if not decls:
        return False
    port2canon, canon = {}, f
    for alias, port, _ in sorted(decls, key=lambda d: -len(d[0])):
        c = port2canon.setdefault(port, f"A{len(port2canon)}")
        canon = re.sub(r"\b%s\b" % re.escape(alias), c, canon)
    return bool(_TAUT_SELF_F.match(canon))


from llm import LLMError
from critic import critique

MAX_AGENT_CALLS = ps.CONFIG["max_agent_calls"]
LLM_MAX_RETRIES = 10                    # LLM 瞬时故障退避重试上限
SEARCH_MODE = ps.CONFIG.get("search_mode", "dfs")   # dfs | bfs
VERIFY_MODE = ps.CONFIG.get("verify_mode", "standard")  # standard | bmc_first
ABORT_ON_FRAMEWORK_ERROR = ps.CONFIG.get("abort_on_framework_error", True)
FRAMEWORK_ERROR_PATTERNS = ps.CONFIG.get("framework_error_patterns", [])

REPORT = Path(__file__).resolve().parents[1] / "results"


class Dispatcher:
    def __init__(self, hierarchy_path: str, property_path: str,
                 reader: DesignReader = None, verifier=cha_verify.cha_verify,
                 priors_path: str = None):
        self.h = Hierarchy.load(hierarchy_path)
        # src 路径相对 riscv-mini 根（= AGVerify 的上级）
        self.reader = reader or ChiselFileReader(
            self.h, src_root=str(Path(__file__).resolve().parents[2]))
        prop = json.loads(Path(property_path).read_text(encoding="utf-8"))
        self.prop = prop
        self.st = ps.ProofState(self.h, self.reader, prop)
        self._raw_verifier = verifier     # 原始验证器(记忆化旁路用)
        self._verify_memo = {}            # 验证记忆: 键=公式+前提集+模块+引擎
        self._memo_hits = 0
        self.verifier = self._memo_verifier   # 注入便于测试 mock(经记忆化)
        # 先验知识（公理）: spec/priors.json, 按 module 分组
        self.priors = {}
        if priors_path is None:
            cand = Path(hierarchy_path).parent / "priors.json"
            priors_path = str(cand) if cand.exists() else None
        if priors_path and Path(priors_path).exists():
            for x in json.loads(Path(priors_path).read_text(
                    encoding="utf-8")):
                self.priors.setdefault(x["module"], []).append(x)
        # 本次运行的结果子目录: 懒创建（run() 时才建, 调试实例化不产生垃圾目录）
        self.run_dir = REPORT / time.strftime("run_%Y%m%d_%H%M%S")
        self._dirs_ready = False
        # 先验烘焙为 *Prop 类常驻 chaAssume; 信号编号全局唯一
        self._num = 0
        self.priors_by_module = {}
        prior_ids = []
        for m, xs in self.priors.items():
            sigs, formulas = [], []
            seen = {}                 # 同模块先验共享别名只声明一次
            for x in xs:
                formulas.append(x["formula"])
                prior_ids.append(x["id"])
                for local, s in x["signals"].items():
                    if local in seen:
                        if seen[local] != s["port"]:
                            raise ValueError(
                                f"先验信号 {local} 在模块 {m} 内路径冲突: "
                                f"{seen[local]} vs {s['port']}")
                        continue
                    seen[local] = s["port"]
                    self._num += 1
                    sigs.append((local, ps.ProofState.signal_path(s), self._num))
            self.priors_by_module[m] = {"signals": sigs,
                                        "assumes": formulas}
        self.report = {"rounds": 0, "conclusion": None, "events": [],
                       "priors_used": prior_ids}
        self.agent_calls = 0
        # 通路引导全局记录: node_id → ctx 块(不挂在 node 对象上);
        # 回滚时删除并按新公式重算替换
        self._pg_records = {}
        # 回滚提醒: node_id → 提醒文本(下轮分解时注入 ctx 后清除)
        self._rollback_notices = {}
        # RTL 压缩: 语法错误样本(连续>=2 触发重压缩) 与缓存键
        self._rtl_errors = []
        self._rtl_key = None

    # ------------------------------------------------------------------
    # 信号/性质 → cha_verify 参数
    # ------------------------------------------------------------------

    def _materialize(self, sources: List) -> Tuple[List, List[str]]:
        """公式+信号源列表 → (信号声明, 公式列表), 别名冲突重命名。

        sources: [(formula, {别名: (module, port)}), ...]
        同别名同信号 → 复用首次声明(不重复声明, 公式不变)
        同别名不同信号 → 重命名 别名_2/_3... 并改写该公式中的引用
        """
        import re as _re
        decls: List[Tuple[str, str, int]] = []
        # 别名 -> (模块, 路径): 键含 module 维度(2026-10-06 同名不同网修复
        # ——run_20261006_173520 实证: MemArbiter.io.nasti.ar.ready 与
        # DCache.io.nasti.ar.ready 裸路径相同但非同一网络, 只比 path 会
        # 把不同网络并成一个槽/声明, 检查一由此平凡通过)
        bound: Dict[str, Tuple[str, str]] = {}
        formulas: List[str] = []
        for formula, sigs in sources:
            rename = {}
            for alias, (mod, port) in sigs.items():
                key = (mod, port)
                if alias in bound:
                    if bound[alias] == key:
                        continue            # 同信号, 复用声明
                    # 同名不同信号(含同名不同网) → 重命名
                    i = 2
                    while f"{alias}_{i}" in bound:
                        i += 1
                    new_alias = f"{alias}_{i}"
                    bound[new_alias] = key
                    rename[alias] = new_alias
                else:
                    bound[alias] = key
            # 改写公式中的别名引用(整词匹配)
            for old, new_a in rename.items():
                formula = _re.sub(r"\b%s\b" % _re.escape(old), new_a, formula)
            formulas.append(formula)   # G 语义由 chaAssert 全局检查提供, 不额外包装
        # 统一生成声明(编号全局唯一) — decls 的 path 字段保留裸路径
        # (cha_verify 生成 val alias = path 在宿主模块类内, 模块由 run_at 决定)
        for alias, (mod, port) in bound.items():
            self._num += 1
            decls.append((alias, port, self._num))
        return decls, formulas

    def _node_sources(self, node, with_assumes: bool = True) -> List:
        """节点(+其 assume/children)的公式+信号源列表"""
        def _path(s):
            # expr 信号: 表达式即生成端 path (val alias = expr)
            p = s.get("port") or ""
            if p.startswith("expr:") or not p:
                e = (s.get("expr") or "").strip()
                if not e or "?" in e or ":" in e and not e.startswith("io."):
                    raise SignalGenError(
                        f"信号缺少合法 port/expr (module={s.get('module')}, "
                        f"port={s.get('port')!r}, expr={s.get('expr')!r})")
                return e
            return p

        sources = [(node.formula,
                    {a: (s["module"], _path(s))
                     for a, s in (node.derived.get("signals")
                                  or node.signals).items()})]
        if with_assumes:
            for aid in node.assumes:
                a = self.st.nodes[aid]
                sources.append((a.formula,
                                {k: (s["module"], _path(s))
                                 for k, s in (a.signals or {}).items()}))
        return sources

    def _assume_formulas(self, node) -> List[str]:
        return [self.st.nodes[a].formula for a in node.assumes]

    # ------------------------------------------------------------------
    # 验证执行
    # ------------------------------------------------------------------

    def _record_outcome(self, node_id, phase, raw, module=None):
        if not hasattr(self, "_outcome_records"):
            self._outcome_records = []
        import time as _time
        self._outcome_records.append(
            {"node": node_id, "phase": phase, "module": module,
             "verdict": raw.get("verdict", ""),
             "detail": raw.get("detail", ""),
             "_ts": _time.strftime("%H:%M:%S")})
        """运行时结果账本(outcomes.jsonl): 逐性质逐阶段记录,
        SUMMARY 直接读取, 不再事后对账。"""
        import json as _json
        node = self.st.nodes.get(node_id)
        if node is None:
            return
        rec = {"ts": time.strftime("%H:%M:%S"), "node": node_id,
               "phase": phase,                       # global_bmc/module_bmc/module_ic3/compile
               "module": module or (node.derived.get("module")),
               "formula": node.formula,
               "verdict": raw.get("verdict"),
               "detail": (raw.get("detail") or "")[:200]}
        try:
            with open(self.run_dir / "outcomes.jsonl", "a",
                      encoding="utf-8") as f:
                f.write(_json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _conclusion_input_guard(self, task, node_id) -> bool:
        """结论输入守卫(2026-10-06, 保守): 蕴含结论为**单一信号原子**(可带!)
        且该信号在目标模块为 Input(自由输入) → 本模块永不可证, 当场拒绝并
        反馈路由到 writer 模块。保守边界: 结论为布尔组合/expr/多信号一律
        不触发; 查不到方向不触发。返回 True=已拦截。"""
        st = self.st
        node = st.nodes[node_id]
        f = node.formula or ""
        if "->" not in f:
            return False
        concl = f.split("->", 1)[1].strip()
        # 剥时态包装 F/G/X 与 U 右端: 结论取最外层时态算子的核
        while True:
            c2 = concl.strip()
            m = re.match(r"^([FGX])\s*\(?\s*(.+?)\s*\)?\s*$", c2)
            if not m or m.group(2).count("(") != m.group(2).count(")"):
                break
            concl = m.group(2)
        # U 的右支作为结论核
        if " U " in concl or ")U" in concl.replace(" ", ""):
            concl = re.split(r"\s+U\s+|\)U|U\(", concl.replace(" ", ""))[-1]
        # 提取结论中全部信号原子(支持布尔组合; 2026-10-09 用户放宽:
        # 单原子 → 全原子都是 Input 才触发, 混合方向不触发)
        atoms = set(re.findall(
            r"!?([A-Za-z_]\w*)", concl.replace(" ", "")))
        atoms -= {"G", "F", "X", "U"}          # 排除时态算子
        if not atoms:
            return False                       # 无信号原子
        # 逐原子检查方向: 全部是 Input 才触发
        all_input = True
        writers = []
        for alias in atoms:
            sdef = (node.signals or {}).get(alias) or {}
            if not sdef.get("port"):
                all_input = False              # expr 定义: 不触发
                break
            mod = sdef.get("module")
            if not mod:
                all_input = False
                break
            try:
                if st.reader.port_direction(mod, sdef["port"]) != "Input":
                    all_input = False          # 有一个是 Output → 不触发
                    break
            except Exception:
                all_input = False
                break
            # 收集 writer 视图
            try:
                wid = ps.wire_id_of(sdef, st.h)
                ent = st.registry.entries.get(wid)
                for v in (getattr(ent, "views", None) or ()):
                    vm, _, vp = v.partition(".")
                    try:
                        if st.reader.port_direction(vm, vp) == "Output":
                            writers.append(v)
                    except Exception:
                        pass
            except Exception:
                pass
        return all_input

    def _ltl_syntax_check(self, formula: str) -> Optional[str]:
        """LTL 语法预检(2026-10-06, 保守): 语法铁律的正则快查, 命中即免跑
        sbt 直接回编译错。返回错误描述或 None。仅查确凿违规。"""
        f = formula
        # R2: ## 与性质层算子直接相邻
        if re.search(r"##\d*\s*\(?\s*[FGXU]\b", f) or \
           re.search(r"\b[FGXU]\s*\)?\s*##", f):
            return "## 操作数触及性质层算子(F/G/X/U)"
        # R1: ## 序列层出现双字符布尔(启发式: ## 前后最近的括号段内)
        for m in re.finditer(r"##\s*\d*", f):
            seg_l = f[max(0, m.start() - 30):m.start()]
            seg_r = f[m.end():m.end() + 30]
            if re.search(r"&&|\|\|", seg_l.split("(")[-1]) or \
               re.search(r"&&|\|\|", seg_r.split(")")[0]):
                return "## 序列层出现 && / ||(应为单字符 & / |)"
        # R3: -> 出现在 ## 任一紧邻操作数内
        if re.search(r"->[^#]{0,20}##|##\s*\d*\s*[^#]{0,20}->", f):
            return "## 操作数内出现 ->"
        return None

    def batch_ic3_verify(self):
        """bmc_first 模式的批量 IC3 验证 (2026-10-08):
        树闭合后对全部 BMC 级 KB 条目对应的节点逐个跑 IC3。
        全过 → KB 条目升级 proof_strength="ic3", 节点标 IC3_PROVEN。
        有败 → 从 KB 剔除该条目 + 节点标 BMC_FAILED + 回滚其父。
        返回 (总数, 成功数)。"""
        if VERIFY_MODE != "bmc_first":
            return (0, 0)
        st = self.st
        bmc_entries = [e for e in st.kb.entries
                       if e.proof_strength == "bmc"]
        total = len(bmc_entries)
        ok = 0
        for e in bmc_entries:
            nid = e.node_origin
            node = st.nodes.get(nid)
            if node is None:
                st.kb.remove(e.kid)
                continue
            raw = self.verifier(
                module=node.derived.get("module") or
                self.prop_module(node),
                signals=self._materialize(
                    self._node_sources(node))[0],
                assert_formula=node.formula,
                assumes=self._materialize(
                    self._node_sources(node))[1][1:],
                mode="ic3",
                priors_by_module=self.priors_by_module)
            self._record_outcome(nid, "batch_ic3", raw,
                                 node.derived.get("module"))
            if raw.get("verdict") == "PASS":
                e.proof_strength = "ic3"
                st.mark(nid, ps.IC3_PROVEN)
                ok += 1
            else:
                st.kb.remove(e.kid)
                st.mark(nid, ps.BMC_FAILED)
                st.record_failure(nid, "VIOLATED",
                                  cause="BATCH_IC3_FAIL",
                                  evidence=f"批量IC3发现反例: "
                                           f"{node.formula[:60]}")
                self.report["events"].append(
                    f"{nid}: 批量IC3 FAIL, 从KB剔除 {e.kid}")
        self.report["batch_ic3"] = {"total": total, "passed": ok}
        return (total, ok)

    def _kb_path_filter(self, node, passed):
        """KB 通路过滤 (2026-10-10 用户语义): CONJUNCT 蕴含检查的 KB 复用
        基于条目间信号连通性——从目标+已过子性质的信号出发, 经 KB 条目间
        共享网络做传递闭包, 只保留可连通的条目。返回 KBEntry 列表。"""
        st = self.st
        # 初始信号集: 目标信号 + 已过子性质的信号
        wire_set = set()
        try:
            wire_set |= {ps.wire_id_of(x, st.h)
                         for x in (node.signals or {}).values()}
        except Exception:
            pass
        for n in passed:
            try:
                wire_set |= {ps.wire_id_of(x, st.h)
                             for x in (n.signals or {}).values()}
            except Exception:
                pass
        if not wire_set:
            return []   # 无信号锚点, 不过滤(保守返回空)
        # 传递闭包: 反复扫描 KB, 有新连通就扩展
        included = []
        included_ids = set()
        changed = True
        while changed:
            changed = False
            for e in st.kb.entries:
                if id(e) in included_ids:
                    continue
                try:
                    ew = {ps.wire_id_of(x, st.h)
                          for x in (e.signals or {}).values()}
                except Exception:
                    continue
                if ew & wire_set:
                    included.append(e)
                    included_ids.add(id(e))
                    wire_set |= ew
                    changed = True
        return included

    def _build_proof_tree(self):
        """层次化证明恢复 (2026-10-10): SUCCESS 后自动构建证明树.

        流程:
        1. 从根出发计算传递依赖闭包(证明链)
        2. 对链上每个节点做记忆化消融(BMC, 逐条移除 KB 前提)
        3. 自顶向下渲染证明树 + 性质明细表

        返回 markdown 字符串(追加到 SUMMARY).
        """
        st = self.st
        nodes = st.nodes
        kb_map = {e.kid: e for e in st.kb.entries}
        root_id = st.root

        # ── 1. 传递依赖闭包 ──
        chain = {}

        def _collect(node_id, depth=0):
            if node_id in chain or depth > 20:
                return
            n = nodes.get(node_id)
            if n is None or n.status != ps.IC3_PROVEN:
                return
            kb_used = self._get_node_kb_deps(node_id)
            module = n.derived.get("module") or self.prop_module(n)
            # 旧格式 fallback: 无 [KB:T...] 标签时, 用 broad 模式获取可见条目
            # 时序过滤: 只含此节点验证之前已入 KB 的条目(防循环)
            if not kb_used:
                kb_srcs = self._kb_premises_for(n, module, broad=True)
                all_kids = [src[2] for src in kb_srcs if len(src) > 2]
                # 获取此节点的验证时间
                node_ts = None
                for rec in reversed(getattr(self, "_outcome_records", [])):
                    if (rec.get("node") == node_id
                            and rec.get("phase") == "module_ic3"):
                        node_ts = rec.get("_ts", "")
                        break
                if node_ts:
                    # KB 条目按 node_origin 的验证时间过滤
                    kb_used = []
                    for kid in all_kids:
                        e = next((x for x in st.kb.entries
                                  if x.kid == kid), None)
                        if e is None:
                            continue
                        # 条目来源节点的验证时间
                        e_ts = None
                        for rec in reversed(
                                getattr(self, "_outcome_records", [])):
                            if (rec.get("node") == e.node_origin
                                    and rec.get("phase") == "module_ic3"
                                    and rec.get("verdict") == "PASS"):
                                e_ts = rec.get("_ts", "")
                                break
                        # 只包含早于此节点的条目
                        if e_ts is None or e_ts < node_ts:
                            kb_used.append(kid)
                else:
                    kb_used = all_kids
            chain[node_id] = {
                "formula": n.formula, "module": module,
                "kb_used": kb_used, "kind": n.kind,
            }
            for kid in kb_used:
                if kid in kb_map:
                    _collect(kid, depth + 1)
            for c in (n.children or []):
                _collect(c, depth + 1)
            for a in (n.assumes or []):
                an = nodes.get(a)
                if an:
                    did = an.discharged_by
                    if did:
                        _collect(did, depth + 1)

        _collect(root_id)
        if not chain:
            return None

        # ── 2. 记忆化消融 ──
        ablation_cache = {}
        do_ablation = ps.CONFIG.get("proof_tree_ablate", True)

        def _ablate_node(node_id):
            if node_id in ablation_cache:
                return ablation_cache[node_id]
            info = chain.get(node_id)
            if not info or not info["kb_used"]:
                ablation_cache[node_id] = []
                return []
            n = nodes.get(node_id)
            if n is None:
                ablation_cache[node_id] = info["kb_used"]
                return info["kb_used"]

            module = info["module"]
            remaining = list(info["kb_used"])

            for kid in sorted(info["kb_used"], reverse=True):
                trial = [k for k in remaining if k != kid]
                if not trial:
                    continue
                result = self._ablation_bmc(n, module, trial, kb_map)
                if result == "PASS":
                    remaining = trial
                    self.report["events"].append(
                        f"消融: {node_id} <- {kid} 冗余")
                else:
                    self.report["events"].append(
                        f"消融: {node_id} <- {kid} 必要({result})")

            ablation_cache[node_id] = remaining
            return remaining

        if do_ablation:
            for nid in sorted(chain, key=lambda x: (0, x) if x.startswith("T")
                              else (1, x)):
                _ablate_node(nid)
        else:
            # 不消融时直接用全集
            for nid in chain:
                ablation_cache[nid] = chain[nid]["kb_used"]

        # ── 2b. 充分性消融 (ASSUME 节点的有效性检查) ──
        # 对 ASSUME 节点: "假设 + 设计 + KB[子集] ⊢ 目标" 的 KB 依赖
        validity_cache = {}
        if do_ablation:
            for nid in sorted(chain):
                info = chain[nid]
                n = nodes.get(nid)
                if n is None or n.kind != "assert":
                    continue
                # 检查是否有 assume_validity 的 outcome
                has_validity = any(
                    r.get("node") == nid and "validity" in str(r.get("phase", ""))
                    for r in getattr(self, "_outcome_records", []))
                if not has_validity or not info["kb_used"]:
                    continue

                # 充分性消融: 逐条移除 KB, 重跑 assume_validity
                module = info["module"]
                v_remaining = list(info["kb_used"])
                for kid in sorted(info["kb_used"], reverse=True):
                    trial = [k for k in v_remaining if k != kid]
                    if not trial:
                        continue
                    result = self._ablation_validity(n, module, trial, kb_map)
                    if result == "PASS":
                        v_remaining = trial
                        self.report["events"].append(
                            f"充分性消融: {nid} <- {kid} 冗余")
                    else:
                        self.report["events"].append(
                            f"充分性消融: {nid} <- {kid} 必要({result})")
                validity_cache[nid] = v_remaining

        # ── 3. 渲染 ──
        L = ["\n## 7. 层次化证明树\n"]

        def _render(node_id, indent, visited):
            if node_id in visited:
                L.append("  " * indent + "(ref) " + node_id)
                return
            visited.add(node_id)
            pad = "  " * indent

            if node_id in kb_map:
                e = kb_map[node_id]
                minimal = ablation_cache.get(node_id, [])
                L.append(pad + f"[{e.kid}] `{e.formula[:55]}`"
                         + f" @{e.proven_at or '?'}")
                for kd in sorted(minimal):
                    _render(kd, indent + 1, visited)
            elif node_id in chain:
                info = chain[node_id]
                minimal = ablation_cache.get(node_id, info["kb_used"])
                n = nodes.get(node_id)
                L.append(pad + f"{node_id}: `{info['formula'][:50]}`"
                         + f" @{info['module']}")
                for kd in sorted(minimal):
                    _render(kd, indent + 1, visited)
                if n:
                    for c in (getattr(n, 'children', None) or []):
                        _render(c, indent + 1, visited)
                    for a in (getattr(n, 'assumes', None) or []):
                        an = nodes.get(a)
                        if an:
                            L.append("  " * (indent + 1)
                                     + f"ASSUME: `{an.formula[:45]}`")
                            did = getattr(an, 'discharged_by', None)
                            if did:
                                _render(did, indent + 2, visited)

        _render(root_id, 0, set())

        # 性质明细表
        L.append("\n### 性质明细\n")
        L.append("| 标签 | 性质 | 验证模块 | 最小依赖 |")
        L.append("|---|---|---|---|")
        for nid in sorted(chain):
            info = chain[nid]
            minimal = ablation_cache.get(nid, [])
            if nid in kb_map:
                e = kb_map[nid]
                # 跨模块标注: 找谁使用了此条目
                used_at = set()
                for other_id, other_info in chain.items():
                    if nid in other_info.get("kb_used", []):
                        other_mod = other_info.get("module", "?")
                        if other_mod != (e.proven_at or "?"):
                            used_at.add(other_mod)
                cross = f" → 使用@{','.join(used_at)}" if used_at else ""
                v_min = validity_cache.get(nid, [])
                v_str = f"; 充分性: {', '.join(v_min)}" if v_min else ""
                L.append(f"| {e.kid} | `{e.formula[:40]}`"
                         + f" | {e.proven_at or '?'}{cross}"
                         + f" | {', '.join(minimal) or '(先验)'}{v_str} |")
            else:
                L.append(f"| {nid} | `{info['formula'][:40]}`"
                         + f" | {info['module']}"
                         + f" | {', '.join(minimal) or '(先验)'} |")

        return "\n".join(L)

    def _get_node_kb_deps(self, node_id):
        """从 outcome 记录提取某节点的 KB 依赖([KB:...] 标签)."""
        import re as _re
        for rec in reversed(getattr(self, "_outcome_records", [])):
            if (rec.get("node") == node_id
                    and rec.get("verdict") == "PASS"
                    and rec.get("phase") == "module_ic3"):
                detail = str(rec.get("detail", ""))
                m = _re.search(r'\[KB:([T0-9,]+)\]', detail)
                if m:
                    return m.group(1).split(",")
                return []
        return []

    def _ablation_bmc(self, node, module, kb_kids, kb_map):
        """消融 BMC: 用指定 KB 子集重跑模块 BMC."""
        try:
            sources = self._node_sources(node)
            for kid in kb_kids:
                e = kb_map.get(kid)
                if e is None:
                    continue
                ports = {}
                okvis = True
                for al, x in (e.signals or {}).items():
                    wid = ps.wire_id_of(x, self.st.h)
                    ent = self.st.registry.entries.get(wid)
                    v = next((t for t in (getattr(ent, "views", None) or [])
                              if t.startswith(str(module) + ".")), None)
                    if v is None:
                        okvis = False
                        break
                    ports[al] = (str(module), v.split(".", 1)[1])
                if okvis:
                    sources.append((e.formula_raw or e.formula, ports))

            decls, formulas = self._materialize(sources)
            raw = self.verifier(
                module=module, signals=decls,
                assert_formula=formulas[0],
                assumes=formulas[1:],
                mode="bmc",
                priors_by_module=self.priors_by_module)
            self._record_outcome(node.id, "ablation_bmc", raw, module)
            return raw.get("verdict", "?")
        except Exception as e:
            return "ERROR:" + str(e)[:30]

    def _ablation_validity(self, node, module, kb_kids, kb_map):
        """充分性消融 BMC: 用指定 KB 子集重跑 assume_validity."""
        try:
            sources = self._node_sources(node, with_assumes=True)
            for kid in kb_kids:
                e = kb_map.get(kid)
                if e is None:
                    continue
                ports = {}
                okvis = True
                for al, x in (e.signals or {}).items():
                    wid = ps.wire_id_of(x, self.st.h)
                    ent = self.st.registry.entries.get(wid)
                    v = next((t for t in (getattr(ent, "views", None) or [])
                              if t.startswith(str(module) + ".")), None)
                    if v is None:
                        okvis = False
                        break
                    ports[al] = (str(module), v.split(".", 1)[1])
                if okvis:
                    sources.append((e.formula_raw or e.formula, ports))

            decls, formulas = self._materialize(sources)
            raw = self.verifier(
                module=module, signals=decls,
                assert_formula=formulas[0],
                assumes=formulas[1:],
                mode="bmc",
                priors_by_module=self.priors_by_module)
            self._record_outcome(node.id, "ablation_validity", raw, module)
            return raw.get("verdict", "?")
        except Exception as e:
            return "ERROR:" + str(e)[:30]

    def _kb_premises_for(self, node, module, broad=True):
        """KB 默认前提 (2026-10-10 用户语义修订):
        broad=True (检查二/module_ic3): 只检查可见性——凡能在本模块
        落地的 KB 条目都烘入, 不限上限, 不要求与目标共享网络。
        broad=False (保留接口): 旧模式, 相关性+可见性+上限。"""
        if not ps.CONFIG.get("kb_as_premises", True):
            return []
        st = self.st
        if not broad:
            try:
                cur_wires = {ps.wire_id_of(x, st.h)
                             for x in (node.signals or {}).values()}
            except Exception:
                return []
        out = []
        for e in st.kb.entries:
            try:
                esigs = e.signals or {}
                if not broad:
                    ew = {ps.wire_id_of(x, st.h) for x in esigs.values()}
                    if not ew or not (ew & cur_wires):
                        continue
                ports = {}
                okvis = True
                for al, x in esigs.items():
                    wid = ps.wire_id_of(x, st.h)
                    ent = st.registry.entries.get(wid)
                    v = next((t for t in (getattr(ent, "views", None) or ())
                              if t.startswith(str(module) + ".")), None)
                    if v is None:
                        okvis = False
                        break
                    port_part = v.split(".", 1)[1]
                    if port_part.startswith("expr:"):
                        expr = (x.get("expr") or port_part[5:]).strip()
                        if not expr:
                            okvis = False
                            break
                        ports[al] = (str(module), expr)
                    else:
                        ports[al] = (str(module), port_part)
                if okvis:
                    out.append((e.formula, ports, e.kid))
            except Exception:
                continue
        if not broad:
            return out[:int(ps.CONFIG.get("kb_premises_max", 8))]
        return out  # broad: 不限上限, 含 kid

    def _memo_verifier(self, module, signals, assert_formula, assumes,
                       mode, run_at=None, **kw):
        """验证记忆化 (2026-10-06): 验证结果是 (公式, 前提集, 模块, 引擎,
        信号映射) 的确定函数——同键重验必得同结论(MODULE_STUCK 重入队反复
        重演同一验证的浪费源)。命中回放缓存结论不跑 sbt; 前提集变化键自动
        变化, 无失效风险; run 内有效(设计不变), 跨 run 持久化留待 KB 一起。"""
        def _norm(x):
            return re.sub(r"\s+", "", str(x or ""))
        if isinstance(signals, dict):
            sig_items = tuple(sorted(
                (al, str(s.get("module")),
                 str(s.get("port") or s.get("expr")))
                for al, s in signals.items()))
        else:                       # decls 列表形态(_materialize 产物)
            sig_items = tuple(str(x) for x in (signals or []))
        key = (str(module), str(mode), _norm(assert_formula),
               tuple(sorted(_norm(a) for a in (assumes or []))),
               sig_items, str(run_at or ""), VERIFY_MODE)
        hit = self._verify_memo.get(key)
        if hit is not None:
            self._memo_hits += 1
            out = dict(hit)
            out["detail"] = (f"[缓存命中: 同键先前 {hit.get('_ts', '')} "
                             f"{hit.get('verdict')}] " + str(out.get("detail", "")))
            out.pop("_ts", None)
            return out
        raw = self._raw_verifier(module=module, signals=signals,
                                 assert_formula=assert_formula,
                                 assumes=assumes, mode=mode,
                                 run_at=run_at, **kw)
        if isinstance(raw, dict):
            store = dict(raw)
            store["_ts"] = time.strftime("%H:%M:%S")
            self._verify_memo[key] = store
        return raw

    def run_bmc_filter(self, node_id) -> Dict:
        """全局 Tile BMC 筛选: assert 住归属模块的 *Prop 类(模块视角
        路径), verify 运行在 Tile(实例化全部子类, 真实环境+先验常驻)"""
        node = self.st.nodes[node_id]
        syn = self._ltl_syntax_check(node.formula or "")
        if syn:
            return {"verdict": "ERROR",
                    "detail": f"LTL 语法预检: {syn}"}
        home = node.derived.get("module") or self.prop_module(node)
        try:
            decls, formulas = self._materialize(self._node_sources(
                node, with_assumes=False))
        except SignalGenError as e:
            return {"verdict": "ERROR", "detail": f"信号生成错误: {e}"}
        if _trivially_true(formulas[0], decls):
            return {"verdict": "PASS",
                    "detail": "平凡真: 同网络退化 A -> F A, 免求解"}
        return self.verifier(
            module=home,
            signals=decls,
            assert_formula=formulas[0],
            assumes=[],
            mode="bmc",
            priors_by_module=self.priors_by_module,
            run_at="Tile")

    def run_module_ic3(self, node_id) -> Dict:
        """模块级验证（两段式: BMC 先行拿反例波形 → IC3 完备）。
        BMC FAIL 时 critic 可索引模块级反例 VCD（模块作用域内的
        失败时序）; PASS 才进 IC3。"""
        node = self.st.nodes[node_id]
        syn = self._ltl_syntax_check(node.formula or "")
        if syn:
            self._record_outcome(node_id, "module_bmc", {"verdict": "ERROR",
                                 "detail": f"LTL 语法预检: {syn}"},
                                 node.derived.get("module") or
                                 self.prop_module(node))
            return {"verdict": "ERROR",
                    "detail": f"LTL 语法预检: {syn}"}
        module = node.derived.get("module") or self.prop_module(node)
        try:
            decls, formulas = self._materialize(self._node_sources(node))
        except SignalGenError as e:
            return {"verdict": "ERROR", "detail": f"信号生成错误: {e}"}
        # KB 默认前提: 相关且可见的已证定理并入 assume 集(溯源记入明细)
        kb_srcs = self._kb_premises_for(node, module)
        kb_kids = []
        if kb_srcs:
            try:
                n_own = len(formulas)
                decls, formulas = self._materialize(
                    self._node_sources(node)
                    + [src[:2] for src in kb_srcs])
                kb_used = formulas[n_own:]
                kb_kids = [src[2] for src in kb_srcs]
            except SignalGenError:
                kb_used = []
        else:
            kb_used = []
        kb_tag = f" [KB:{','.join(kb_kids)}]" if kb_kids else ""
        if _trivially_true(formulas[0], decls):
            return {"verdict": "PASS",
                    "detail": "平凡真: 同网络退化 A -> F A, 免求解" + kb_tag}
        common = dict(
            module=module,
            signals=decls,
            assert_formula=formulas[0],
            assumes=formulas[1:],
            priors_by_module=self.priors_by_module)
        raw = self.verifier(mode="bmc", **common)
        if kb_tag and isinstance(raw, dict):
            raw = dict(raw)
            raw["detail"] = str(raw.get("detail", "")) + kb_tag
        self._record_outcome(node_id, "module_bmc", raw, module)
        if raw.get("verdict") != "PASS":
            # 模块 BMC 失败: assume 兑现节点 → 先试候选模块(writer 优先)
            if getattr(node, "locked_conjunct", False) \
                    and self._try_alternate_modules(node_id):
                return {"verdict": "PASS", "detail": "多落点: 候选模块证毕"}
            return raw                     # 带模块级反例波形
        # bmc_first 模式 (2026-10-08): 只跑 BMC, 跳过 IC3(延后批量)
        if VERIFY_MODE == "bmc_first":
            return {"verdict": "PASS",
                    "detail": str(raw.get("detail", "")) +
                              " [bmc_first: IC3 deferred]"}
        raw2 = self.verifier(mode="ic3", **common)
        if raw2.get("verdict") == "PASS":
            node._ic3_verified = True    # 真正过了 IC3 的标记
        # 条件标记: 假设未全部兑现的证毕是【条件证毕】(账本/展示须区分)
        if raw2.get("verdict") == "PASS":
            asm = [self.st.nodes[self.st.nodes[a].discharged_by]
                   for a in (getattr(node, "assumes", None) or [])
                   if self.st.nodes[a].discharged_by in self.st.nodes]
            raw2 = dict(raw2)
            raw2["conditional"] = bool(
                [d for d in asm if d.status != ps.IC3_PROVEN])
        if kb_tag and isinstance(raw2, dict):
            raw2 = dict(raw2)
            raw2["detail"] = str(raw2.get("detail", "")) + kb_tag
        self._record_outcome(node_id, "module_ic3", raw2, module)
        if raw2.get("verdict") != "PASS" \
                and getattr(node, "locked_conjunct", False) \
                and self._try_alternate_modules(node_id):
            return {"verdict": "PASS", "detail": "多落点: 候选模块证毕"}
        return raw2

    def _run_implication_premises(self, node_id, premise_srcs) -> Dict:
        """空设计蕴含(两段式 BMC→IC3):
        断言=parent 公式; 前提=premise_srcs[(公式, 信号表)]。
        全部来源的信号统一进槽位表(前提引用的信号也声明,
        否则生成 Scala 缺 val → NoSuchMethod)。"""
        node = self.st.nodes[node_id]

        def _smap(sig_dict):
            def p(s):
                port = s.get("port") or ""
                if port.startswith("expr:") or not port:
                    return s.get("expr") or "expr:?"
                return port
            return {a: (s["module"], p(s))
                    for a, s in (sig_dict or {}).items()}

        sources = [(node.formula,
                    _smap(node.derived.get("signals") or node.signals))]
        for f, sigs in premise_srcs:
            sources.append((f, _smap(sigs)))
        decls, formulas = self._materialize(sources)
        premises = [p for p in formulas[1:] if p != node.formula]
        # 槽位键含 module (2026-10-06 同名不同网修复): 不同模块的同名端口
        # 不得共用一个自由输入。alias→(mod,path) 按 sources 序重建
        # (与 _materialize 的重命名后缀一致: 靠同名遍历序还原)
        a2mp = {}
        for _f, sigs in sources:
            for alias, (m, p) in sigs.items():
                a2mp.setdefault(alias, (m, p))
                if a2mp[alias] != (m, p):
                    i = 2
                    while f"{alias}_{i}" in a2mp:
                        i += 1
                    a2mp[f"{alias}_{i}"] = (m, p)
        slot_of: Dict[Tuple[str, str], str] = {}
        wired = []
        for alias, path, num in decls:
            key = a2mp.get(alias, ("?", path))
            if key not in slot_of:
                slot_of[key] = f"io.s{len(slot_of) + 1}"
            wired.append((alias, slot_of[key], num))
        # 两段式
        raw = self.verifier(module="Implication", signals=wired,
                            assert_formula=formulas[0],
                            assumes=premises, mode="bmc")
        if raw.get("verdict") != "PASS":
            return raw
        return self.verifier(module="Implication", signals=wired,
                             assert_formula=formulas[0],
                             assumes=premises, mode="ic3")

    def prop_module(self, node) -> str:
        sigs = node.derived.get("signals") or node.signals
        return next(iter(sigs.values()))["module"]

    # ------------------------------------------------------------------
    # 反馈与回滚
    # ------------------------------------------------------------------

    def _fail(self, node_id, raw, cause):
        node = self.st.nodes[node_id]
        self.agent_calls += 1
        brief = self._module_brief(node)
        fb = critique({
            "node": {"id": node_id, "formula": node.formula,
                     "nl": node.nl, "signals": node.signals,
                     "assert_kind": node.assert_kind},
            "node_role": getattr(node, "sub_owner", None) and "subtask"
                         or node.kind,
            "lineage": self._lineage(node_id),
            "signal_writers": self._signal_writers(node),
            "alt_attempts": self._alt_attempts_for(node_id),
            "module_info": brief["json_part"],
            "__text__": brief["text_part"],
            "strategy": node.strategy,
            "cause": cause,
            "raw_result": {k: v for k, v in raw.items() if k != "vcd"},
            "history": [vars(f) for f in self.st.failures
                        if f.node == node_id][-3:],
            "obligation_reference": self._obligation_ref(node),
        })
        outcome = "VIOLATED" if raw.get("verdict") == "FAIL" else "TIMEOUT"
        level = self.st.record_failure(node_id, outcome, cause,
                                       fb["evidence"], fb["hint"])
        return level

    def _settle(self, node_id):
        """子任务达终态: 父节点 pending-- （不触发轮末——由主循环统一收尾,
        防止多落点等中途事件打断批处理时序）"""
        st = self.st
        owner = getattr(st.nodes.get(node_id), "sub_owner", None)
        if owner and owner in st.nodes and st.nodes[owner].status == ps.PENDING:
            st.nodes[owner].pending_subs -= 1

    def _fail_quiet(self, node_id, raw):
        """BMC 筛选失败: 记账(失败+反KB), 不回滚——反馈留到轮末合并。
        收集到 sub_owner 的 _round_filter_errors 供 BFS 轮末 critic 参考
        (编译错误/违反明细, 优先级低于有效性本身)。"""
        node = self.st.nodes[node_id]
        owner = getattr(node, "sub_owner", None)
        if owner and owner in self.st.nodes:
            o = self.st.nodes[owner]
            if not hasattr(o, "_round_filter_errors"):
                o._round_filter_errors = []
            o._round_filter_errors.append({
                "formula": node.formula,
                "verdict": raw.get("verdict"),
                "detail": (raw.get("detail") or "")[:150]})
        self.agent_calls += 0              # 轮末统一走 critic
        outcome = "VIOLATED" if raw.get("verdict") == "FAIL" else "TIMEOUT"
        self.st.record_failure(node_id, outcome,
                               cause="BAD_DECOMP",
                               evidence=raw.get("detail", ""))
        node = self.st.nodes[node_id]
        if node.status == ps.PENDING:
            node.status = ps.BMC_FAILED       # 筛掉: 终态, 不进有效性前提

    def _round_end_check(self, parent_id):
        """父节点本轮子任务是否全部有结果; 是则执行轮末逻辑"""
        st = self.st
        pnode = st.nodes.get(parent_id)
        if pnode is None or pnode.pending_subs > 0:
            return
        if pnode.status != ps.PENDING:
            return
        # 收集本轮结果
        kids = [st.nodes[c] for c in pnode.children if c in st.nodes]
        asms = [st.nodes[a] for a in pnode.assumes if a in st.nodes]
        subs = [n for n in kids
                + [st.nodes[a.discharged_by] for a in asms
                   if a.discharged_by in st.nodes]
                if n is not None]
        # 未决的(还在栈上/BMC_FILTERED) → 不收尾
        if any(n.status in (ps.PENDING, ps.BMC_FILTERED) for n in subs):
            return
        passed = [n for n in subs if n.status in (ps.IC3_PROVED
                                                  if False else
                                                  (ps.IC3_PROVEN,))]
        failed = [n for n in subs if n.status in (ps.BMC_FAILED, ps.IC3_FAILED)]
        skipped = [n for n in subs if n.status == ps.SKIPPED]

        # 空设计有效性: 前提 = 通过的 children 公式 + 全部 KB 已证 assume
        # + 先验(priors 已烘焙在 Implication 类外, 此处显式并入)
        # ASSUME 策略例外: 模块级充分性已在阶段A由 assume_validity@<模块>
        # 建立(BMC+IC3), 空设计检查对假设组语义不适用——直接视为有效,
        # 走下方模块定案(run_module_ic3 自带 assumes)。
        if pnode.strategy == "ASSUME" and getattr(pnode, "assumes", None):
            valid = {"verdict": "PASS", "detail": "assume_validity 已在阶段A通过"}
        else:
            premise_srcs = [(n.formula, n.signals) for n in passed]
            # KB 通路过滤 (2026-10-10 用户语义): 不是全部 KB, 而是只保留
            # 与目标信号经由 KB 条目间共享网络可连通的条目(传递闭包)
            kb_reachable = self._kb_path_filter(pnode, passed)
            for e in kb_reachable:
                premise_srcs.append((e.formula_raw or e.formula,
                                     e.signals))
            for m, xs in self.priors.items():
                for x in xs:
                    premise_srcs.append((x["formula"], x["signals"]))
            valid = self._validity(parent_id, premise_srcs)
            self._record_outcome(parent_id, "implication", valid, "Implication")
        if self._framework_abort(valid):
            return
        if valid.get("verdict") != "PASS":
            # 轮末合并反馈: 失败明细 + 通过清单
            self._round_feedback(parent_id, failed, skipped, passed, valid)
            return
        # 蕴含先行验证落实 (2026-10-06): 轮末检查一通过置标志
        st.nodes[parent_id]._implication_passed = True
        # 有效 → 父节点模块 IC3 定案(后置)
        raw = self.run_module_ic3(parent_id)
        if self._framework_abort(raw):
            return
        if raw.get("verdict") == "PASS":
            # 健全性门: 模块定案 PASS 只说明"存活 assume 组充分"。
            # 证伪假设先剪除(不构成集合成员); 超时未证的假设须反馈迭代
            # (可能错误或过难)——不可当作清偿。
            self._prune_falsified(parent_id)
            dis = [st.nodes[st.nodes[a].discharged_by]
                   for a in pnode.assumes
                   if st.nodes[a].discharged_by in st.nodes]
            timeout = [d for d in dis if d.status == ps.TIMEOUT_UNPROVED]
            if timeout:
                fb = {"verdict": "FAIL",
                      "detail": "以下假设未能完成证明(可能错误或难以证明, "
                                "请改写为更易证的形式或另提假设): "
                                + "; ".join(d.formula for d in timeout)}
                self._round_feedback(parent_id, failed, skipped, passed, fb)
                return
            if all(d.status == ps.IC3_PROVEN for d in dis):
                st.mark(parent_id, ps.IC3_PROVEN)
                if st.stack and st.stack[-1] == parent_id:
                    st.stack.pop()
                self._promote_ancestors(parent_id)
                # 通过的 children 中需再分解者入队: 逆序压栈保持置信度递减序
                for n in reversed(passed):
                    if n.kind == "assert" and n.status == ps.IC3_PROVEN:
                        if n.children or n.assumes:
                            st.stack.append(n.id)
            else:
                if pnode.status == ps.PENDING:
                    st.mark(parent_id, ps.MOD_PROVEN)
                if st.stack and st.stack[-1] == parent_id:
                    st.stack.pop()
        else:
            self._round_feedback(parent_id, failed, skipped, passed, raw)

    def _validity(self, parent_id, premise_srcs):
        """空设计有效性(两段式 BMC→IC3), 前提为(公式,信号)源列表"""
        return self._run_implication_premises(parent_id, premise_srcs)

    def _record_round(self, parent_id, failed, skipped, passed):
        """轮次结果记入父节点 _rounds(回滚不丢)"""
        node = self.st.nodes.get(parent_id)
        if node is None:
            return
        if not hasattr(node, "_rounds"):
            node._rounds = []
        node._rounds.append({
            "round": len(node._rounds) + 1,
            "proven": [n.formula for n in passed],
            "failed": [n.formula for n in failed],
            "skipped": [n.formula for n in skipped],
        })

    def _round_feedback(self, parent_id, failed, skipped, passed, valid):
        """轮末合并反馈: 全部失败信息 + 通过性质清单 → 重分解"""
        st = self.st
        parts = []
        for n in failed:
            f = next((x for x in st.failures if x.node == n.id), None)
            parts.append(f"未通过: {n.formula}"
                         + (f"（{f.evidence[:80]}）" if f else ""))
        for n in skipped:
            parts.append(f"超限跳过: {n.formula}")
        parts.append(f"当前已证性质尚不足以蕴含目标，需补充覆盖目标前提的性质")
        passed_info = [n.formula for n in passed] or "（无）"
        self.agent_calls += 1
        fb = critique({
            "node": {"id": parent_id, "formula": st.nodes[parent_id].formula,
                     "nl": st.nodes[parent_id].nl,
                     "assert_kind": st.nodes[parent_id].assert_kind},
            "strategy": st.nodes[parent_id].strategy,
            "cause": "ROUND_FAILURE",
            "raw_result": {"verdict": valid.get("verdict"),
                           "detail": "\n".join(parts)},
            "passed_properties": passed_info,
            "kb_available": [e.formula for e in st.kb.entries],
            "round_history": getattr(st.nodes[parent_id], "_rounds", []),
            "history": [vars(f) for f in st.failures
                        if f.node == parent_id][-3:],
            "obligation_reference": self._obligation_ref(
                st.nodes[parent_id]),
        })
        self._record_round(parent_id, failed, skipped, passed)
        st.record_failure(parent_id, "VIOLATED",
                          cause="ROUND_FAILURE",
                          evidence=fb["evidence"], hint=fb["hint"])
        # 轮末失败: 回滚自身(删子树回 PENDING, 原位重分解), 不上溯父链——
        # 各性质失败预算独立计数(fail_count vs 深度预算), 耗尽才放弃
        node = st.nodes[parent_id]
        if node.fail_count >= ps._rollback_allowed(node.depth):
            # 预算耗尽: 该性质 SKIP(不进有效性前提), 父轮正常结算
            st.mark(parent_id, ps.SKIPPED)
            if st.stack and st.stack[-1] == parent_id:
                st.stack.pop()
            self._settle(parent_id)
        else:
            self._rollback(parent_id, "local")
            setattr(node, "_round_started", False)   # 防空轮连锁

    def _rollback(self, node_id, scope="local"):
        """st.rollback + 通路引导记录替换(被删子树清除, 目标作废重算)
        + 回滚提醒(下轮分解显式告知性质可能过强)。"""
        r = self.st.rollback(node_id, scope=scope)
        for did in (r or {}).get("removed", []):
            self._pg_records.pop(did, None)
        self._pg_records.pop(node_id, None)
        self._rollback_notices[node_id] = (
            "该性质的上一轮分解方案已因验证代价耗尽被整体回滚。"
            "这通常意味着某个子性质/assume 可能过强(模块级不可满足或"
            "难以证明)——注意: 该性质本身可能正确, 只是在当前模块/"
            "当前形式下难以兑现。请勿重复同形式: 重新生成分解方案, "
            "或改用更弱/回避式(如 (G !p) -> F q 形态)的前提, 或补充"
            "新的环境 assume。结合 history 中的失败证据分析哪条前提"
            "是瓶颈。")
        return r

    def _rollback_after_fail(self, node_id, level):
        """回滚并弹出受影响的栈任务。返回受影响最深的有效任务 id。"""
        node = self.st.nodes[node_id]
        # 失败发生在分解产物上 → 回滚其分解者; 发生在节点自身 → 回滚自身
        target = node.parent if node.parent else node_id
        if level == "global" and self.st.nodes[target].parent:
            self._rollback(target, scope="global")
        else:
            self._rollback(target, scope="local")
        return target

    # ------------------------------------------------------------------
    # 提升与收尾（unwind）
    # ------------------------------------------------------------------

    def _promote_ancestors(self, node_id):
        """从 node 向上提升: 穿过 assume 节点, MOD_PROVEN 且全部
        assume 已兑现 → IC3_PROVEN"""
        n = self.st.nodes.get(node_id)
        while n and n.parent:
            p = self.st.nodes.get(n.parent)
            if p is None:
                return
            if p.kind == "assume":
                n = p                      # 穿过 assume 继续向上
                continue
            if p.status != ps.MOD_PROVEN:
                return
            if all(self.st.nodes[self.st.nodes[a].discharged_by].status
                   == ps.IC3_PROVEN for a in p.assumes):
                self.st.mark(p.id, ps.IC3_PROVEN)
                n = p
            else:
                return

    def _gc_stack(self):
        """弹出所有已达终态的栈顶任务（连续弹）"""
        while self.st.stack:
            top = self.st.nodes[self.st.stack[-1]]
            if top.status in (ps.IC3_PROVEN, ps.TIMEOUT_UNPROVED):
                self.st.stack.pop()
            else:
                break

    # ------------------------------------------------------------------
    # 主循环
    # ------------------------------------------------------------------

    def _framework_abort(self, raw: Dict) -> bool:
        """框架侧错误识别: 命中签名且开关开启 → 置中止标记。
        框架 bug 重试必然复现, 不应消耗 agent 轮次。"""
        if not (ABORT_ON_FRAMEWORK_ERROR and raw.get("verdict") == "ERROR"):
            return False
        detail = raw.get("detail", "")
        for pat in FRAMEWORK_ERROR_PATTERNS:
            if pat in detail:
                self.report["conclusion"] = "FRAMEWORK_ERROR"
                self.report["events"].append(
                    f"框架错误中止: 命中签名 '{pat}' | {detail[:200]}")
                self._abort = True
                return True
        return False

    def run(self) -> Dict:
        st = self.st
        self._abort = False
        self._llm_retries = 0
        (self.run_dir / "llm_calls").mkdir(parents=True, exist_ok=True)
        (self.run_dir / "sbt").mkdir(parents=True, exist_ok=True)
        llm.set_call_dir(self.run_dir / "llm_calls")
        cha_verify.set_log_dir(self.run_dir / "sbt")
        self._dirs_ready = True
        while st.stack:
            if self._abort:
                break
            if self.agent_calls >= MAX_AGENT_CALLS:
                self.report["conclusion"] = "AGENT_CALLS_EXHAUSTED"
                self.report["events"].append(
                    f"agent 调用数达上限 {MAX_AGENT_CALLS}, 停止")
                break
            # LLM 瞬时故障韧性: 网络抖动等 → 退避重试而非击穿主循环
            try:
                self._step()
            except llm.LLMError as e:
                self._llm_retries += 1
                if self._llm_retries > LLM_MAX_RETRIES:
                    self.report["conclusion"] = "LLM_UNREACHABLE"
                    self.report["events"].append(
                        f"LLM 持续不可达(重试{self._llm_retries}次), 终止: {e}")
                    break
                wait = min(60 * self._llm_retries, 300)
                self.report["events"].append(
                    f"LLM 瞬时故障(第{self._llm_retries}次), {wait}s 后重试: {e}")
                time.sleep(wait)
                continue
            self._llm_retries = 0

        # 层次化证明恢复 (2026-10-10): SUCCESS 后自动构建证明树
        if st.done() and ps.CONFIG.get("proof_tree", True):
            try:
                tree_md = self._build_proof_tree()
                if tree_md:
                    self.report["proof_tree"] = tree_md
            except Exception as e:
                self.report["events"].append(
                    f"证明树构建异常(不影响验证结果): {e}")

        # bmc_first: 树闭合后批量 IC3 验证 (2026-08)
        if VERIFY_MODE == "bmc_first" and st.done():
            total, ok = self.batch_ic3_verify()
            self.report["events"].append(
                f"批量IC3: {ok}/{total} 通过"
                + ("" if ok == total
                   else f", {total-ok} 条剔除并回滚"))
        self.report["agent_calls"] = self.agent_calls
        self.report["done"] = st.done()
        if self.report["conclusion"] is None:
            self.report["conclusion"] = "SUCCESS" if st.done() else "ABORTED"
        self.report["kb"] = [{"id": e.kid, "formula": e.formula}
                             for e in st.kb.entries]
        st.snapshot(str(self.run_dir / "final_proof_state.json"))
        (self.run_dir / "report.json").write_text(
            json.dumps(self.report, ensure_ascii=False, indent=2),
            encoding="utf-8")
        return self.report

    def _step(self):
        """主循环单步(可被 LLMError 打断由 run() 重试)"""
        st = self.st
        self._gc_stack()
        if not st.stack:
            return
        # 统一轮末检查: 栈顶处理完后, 对所有 pending 归零的 PENDING 父节点做轮末
        for nid, n in list(st.nodes.items()):
            if (n.status == ps.PENDING and n.pending_subs == 0
                    and getattr(n, "_round_started", False)):
                self._round_end_check(nid)
        if not st.stack:                 # 轮末可能清空/弹尽栈
            return
        task = st.stack[-1]
        if task not in st.nodes:       # 已被回滚删除(如多落点成功后的轮末回滚)
            st.stack.pop()
            return
        node = st.nodes[task]

        # ---- 激活时 KB 延迟重查 (延迟复用) ----
        # 节点进树后才证毕的定理, 创建时的查重看不见; 弹栈激活时补一次,
        # 命中即免分解/免验证。(反KB 不重查: QUICK_VERIFY_FAIL 等重入队
        # 语义的 VIOLATED 记账也在 neg_kb 里, 激活即杀会破坏递归分解)
        if node.status in (ps.PENDING, ps.BMC_FILTERED):
            try:
                wids = st.registry.wire_ids_of(task)
                hit = st.kb.lookup(node.formula, wids,
                                   signals=node.signals, level=2)
                if hit is not None:
                    st.mark(task, ps.IC3_PROVEN)
                    node.reuse_from = hit.kid
                    if st.stack and st.stack[-1] == task:
                        st.stack.pop()
                    self._promote_ancestors(task)
                    self._settle(task)
                    self._round_end_check(task)
                    return
            except Exception:
                pass                          # 重查失败不阻塞, 走正常流程

        # ---- 阶段 1: PENDING → 分解 ----
        if node.status == ps.PENDING:
            self._decompose(task)
            return

        # ---- 阶段 2: BMC_FILTERED → 模块 IC3 ----
        if node.status == ps.BMC_FILTERED:
            raw = self.run_module_ic3(task)
            self._handle_ic3(task, raw)
            return

        # ---- MOD_PROVEN / 终态: 不应留在栈顶（_gc 已处理） ----
        if node.status == ps.MOD_PROVEN:
            # 等待兑现子任务: 弹出自身（兑现任务在其上）
            st.stack.pop()
            return
        st.stack.pop()          # 兜底

    # ------------------------------------------------------------------

    def _strategy_hint(self, task):
        """多次同模块失败的战略提示 (2026-10-09 用户语义):
        前提: 分解的子性质都在当前模块(未尝试其它模块)
        条件: 同节点连续 ≥3 次分解/验证失败
        提示: ① CONJUNCT → 考虑分解到其它子模块
              ② 否则 → 考虑改用 ASSUME"""
        st = self.st
        node = st.nodes.get(task)
        if not node:
            return None
        fc = node.fail_count
        if fc < 3:
            return None
        # 前提检查: 本轮分解是否有子性质放到了其它模块
        # (有的话说明 agent 已在尝试其它模块, 不需要此提示)
        if getattr(node, "_tried_other_module", False):
            return None
        recent = [f for f in st.failures if f.node == task][-5:]
        causes = {f.cause for f in recent}
        if "CONCLUSION_IS_INPUT" in causes:
            return ("连续多次子性质结论是本模块 Input——CONJUNCT 分解应把 "
                    "子性质放到 writer 模块视角提出, 不要在当前模块反复尝试")
        if any(c in causes for c in ("QUICK_VERIFY_FAIL", "BMC_FAILED",
                                     "MODULE_STUCK")):
            return (f"本模块已连续 {fc} 次分解/验证失败(且子性质都在本模块)——"
                    "请反思: "
                    "① 若选 CONJUNCT, 考虑将子性质分解到其它子模块"
                    "(利用信号等价类跨模块改写); "
                    "② 若子性质确实属于本模块行为约束, 考虑改用 ASSUME "
                    "在本模块引入环境假设后再证明")
        return None

    def _chain_assumes(self, task):
        """3a (2026-10-06): 当前分解链(栈上祖先)的全部存活假设及兑现状态
        ——让 decomposer 看得见"哪些假设已经在用", 勿重复提出。"""
        st = self.st
        out = []
        for nid in dict.fromkeys(st.stack):     # 去重(栈内可能重复)
            n = st.nodes.get(nid)
            if not n:
                continue
            for aid in (getattr(n, "assumes", None) or []):
                a = st.nodes.get(aid)
                if a is None:
                    continue
                d2 = st.nodes.get(a.discharged_by) if a.discharged_by else None
                stat = ("已兑现" if d2 is not None and
                        d2.status == ps.IC3_PROVEN else
                        "兑现中" if d2 is not None and
                        d2.status in (ps.PENDING, ps.BMC_FILTERED) else str(
                            d2.status if d2 else "无兑现节点"))
                out.append({"挂靠": nid, "formula": a.formula, "状态": stat})
        return out

    _SHAPE_RULES = [
        ("互斥/蕴含(安全)", lambda f: "->" not in f.replace(" ", "")),
        ("静默传导 (G s)->FG t",
         lambda f: f.replace(" ", "").startswith("(G")),
        ("停滞前件 (G s)->F t",
         lambda f: "(G" in f.replace(" ", "") and "->F" in
         f.replace(" ", "").replace(" ", "")),
        ("响应公平 s->F t", lambda f: "->F" in f.replace(" ", "")),
        ("响应到达 s->X F t", lambda f: "->XF" in f.replace(" ", "")),
        ("U 形(稳定/参与)", lambda f: " U " in f or "U(" in
         f.replace(" ", "")),
        ("窗口/帧 ##", lambda f: "##" in f),
    ]

    def _kb_family_summary(self):
        """3c (2026-10-06): KB 摘要按模板形状族分组——与模式库同一形状
        语言, 加速"需求→族→已有实例"匹配。"""
        st = self.st
        fam = {}
        for e in st.kb.entries:
            f = e.formula or ""
            f2 = f.replace(" ", "")
            label = "其它"
            for name, rule in self._SHAPE_RULES:
                try:
                    if rule(f):
                        label = name
                        break
                except Exception:
                    pass
            fam.setdefault(label, []).append(
                {"kid": e.kid, "formula": f[:80]})
        return fam

    def _build_ctx(self, task) -> Dict:
        st = self.st
        node = st.nodes[task]
        brief = self._module_brief(node)
        ctx = {
            "待验证性质(当前分解目标, node)": {
                "id": task, "formula": node.formula, "nl": node.nl,
                "signals": node.signals,
                "derived": node.derived,
                "kind": node.kind,
                "assert_kind": node.assert_kind},
            "模块上下文(module_info)": brief["json_part"],
            "__text__": self._rtl_text(node) or brief["text_part"],
            "lineage": self._lineage(task),
            "known_signals": self._known_signals(task),
            "kb": self._kb_family_summary(),
            "neg_kb": st.neg_kb.summary(),
            "链上有效假设(active_assumes)": self._chain_assumes(task),
            "priors": [{"id": x["id"], "module": m, "formula": x["formula"],
                        "nl": x.get("nl", ""), "trusted": x.get("trusted", True)}
                       for m, xs in self.priors.items() for x in xs],
            "round_history": getattr(node, "_rounds", []),
            "策略提示(strategy_hint)": self._strategy_hint(task),
            "history": [vars(f) for f in st.failures if f.node == task][-3:],
            "constraints": {"locked": node.locked_conjunct},
        }
        # 通路引导(义务定位 + 通路族提示): 静态图不可用时静默省略
        blk = self._path_guidance_block(node)
        if blk:
            ctx["通路引导(path_guidance)"] = blk
        # 回滚提醒(一次性消费): 代价耗尽回滚后显式提示重新生成
        notice = self._rollback_notices.pop(task, None)
        if notice:
            ctx["回滚提醒(rollback_notice)"] = notice
        # ctx 体积监测: 超 60KB 警报(健康基线 ~35KB)
        try:
            import json as _j
            sz = len(_j.dumps(ctx, ensure_ascii=False, default=str))
            if sz > 60000:
                msg = "{}: ctx {:.0f}KB 超阈值 60KB".format(task, sz / 1000)
                self.report["events"].append("警报 " + msg)
                ad = Path(self.run_dir) / "ctx_alerts.log"
                ad.parent.mkdir(parents=True, exist_ok=True)
                with open(ad, "a", encoding="utf-8") as f:
                    f.write(time.strftime("%H:%M:%S ") + msg + "\n")
        except Exception:
            pass
        return ctx

    def _path_guidance_block(self, node):
        """PathGuidance 门控块; 任何异常返回 None(零影响降级)。
        块只存于全局记录 self._pg_records(不挂 node), 回滚时替换。"""
        try:
            rec = self._pg_records.get(node.id)
            if rec is not None and rec.get("formula") == node.formula:
                return rec.get("block")
            if not hasattr(self, "_pg"):
                from path_guidance import PathGuidance
                self._pg = PathGuidance()
            if not self._pg.available():
                return None
            blk = self._pg.ctx_block(self.prop_module(node),
                                     node.formula, node.signals)
            self._pg_records[node.id] = {"formula": node.formula,
                                         "block": blk}
            return blk
        except Exception:
            return None

    def _attempt_guard(self, task) -> bool:
        """尝试计数前置: 错误路径同样计入, 超限 SKIP。返回 False=已处理。"""
        st = self.st
        if not st.register_attempt(task):
            st.mark(task, ps.SKIPPED)
            self.report["events"].append(f"{task}: 分解尝试超限, SKIP")
            if st.stack and st.stack[-1] == task:
                st.stack.pop()
            self._settle(task)
            self._round_end_check(task)
            return False
        return True

    def _log_decision(self, task, dec):
        st = self.st
        node = st.nodes[task]
        import json as _json
        items = []
        for it in (dec.get("children") or []) + (dec.get("assumes") or []):
            sigs = {}
            for k, v in (it.get("signals") or {}).items():
                s2 = {"module": v.get("module")}
                if v.get("port"):
                    s2["port"] = v["port"]
                if v.get("expr"):
                    s2["expr"] = v["expr"]
                sigs[k] = s2
            items.append({"formula": it.get("formula"),
                          "signals": sigs})
        rec = {"ts": time.strftime("%H:%M:%S"),
               "kind": "decision", "node": task,
               "goal": node.formula, "goal_nl": node.nl,
               "strategy": dec.get("strategy"), "items": items}
        # 通路引导利用观测: 结构化表态 + rationale 引用检测
        gu = dec.get("guidance_use")
        rat = dec.get("rationale") or ""
        blk = self._pg_records.get(task, {}).get("block") or {}
        fam_names = [f.get('name', '') for f in blk.get('families', [])]
        rec["guidance_use"] = {
            "structured": gu,
            "rationale_refs": [n for n in fam_names if n and n in rat],
            "verdicts_present": [
                v.get('verdict') for v in blk.get('verdicts', [])],
        }
        with open(self.run_dir / "outcomes.jsonl", "a",
                  encoding="utf-8") as f:
            f.write(_json.dumps(rec, ensure_ascii=False,
                                default=str) + "\n")

    def _decompose_or_fail(self, task, ctx, self_rollback=False):
        """调 decompose + 记账; 失败时按预算处理。成功返回决策 dict。
        self_rollback=True(BFS): 失败回滚自身(计数已前置, 耗尽 SKIP);
        False(DFS): 沿用父链回滚语义。"""
        st = self.st
        try:
            self.agent_calls += 1
            dec = decompose(ctx)
            self._log_decision(task, dec)
            return dec
        except DecomposeError as e:
            self.report["events"].append(f"{task}: decomposer 失败 {e}")
            # 附输出片段: 定位 schema 违规的具体位置(4c, 2026-10-06)
            raw_snip = ""
            try:
                raw_snip = " | 原始输出头: " + str(getattr(
                    e, "raw_head", ""))[:160]
            except Exception:
                pass
            st.record_failure(task, "ITER_EXCEED",
                              cause="DECOMPOSER_ERROR",
                              evidence=str(e) + raw_snip)
            if self_rollback:
                node = st.nodes[task]
                if node.fail_count >= ps._rollback_allowed(node.depth):
                    st.mark(task, ps.SKIPPED)
                    if st.stack and st.stack[-1] == task:
                        st.stack.pop()
                    self._settle(task)
                    self._round_end_check(task)
            else:
                self._rollback_after_fail(task, "local")
            return None

    # ------------------------------------------------------------------
    # BFS 模式: 阶段A(前提收集循环: 分解→全局筛→即时快检→有效性)
    #           阶段B(前提逐个验证, 由主循环阶段2+重入队承接, 递归继承BFS)
    # ------------------------------------------------------------------
    def _prune_falsified(self, node_id) -> bool:
        """从 node.assumes 剪除兑现已被 BMC 证伪的假设。
        证伪的假设不构成假设集合成员(不存在"更换"机制)——剪枝后
        有效性/定案/done 自然只对存活集合工作。返回剪枝后是否仍有假设。"""
        node = self.st.nodes[node_id]
        for aid in list(getattr(node, "assumes", None) or []):
            d = self.st.nodes.get(self.st.nodes[aid].discharged_by or "")
            if d is not None and d.status == ps.BMC_FAILED:
                node.assumes.remove(aid)
                self.report["events"].append(
                    f"{node_id}: 假设被证伪剪除 {self.st.nodes[aid].formula}")
        return bool(node.assumes)

    def _decompose_bfs(self, task):
        st = self.st
        node = st.nodes[task]
        while True:
            st.round += 1                    # 轮 = 每次 decomposer 决策
            self.report["rounds"] = st.round
            if not self._attempt_guard(task):
                return
            ctx = self._build_ctx(task)
            # 候选池机制已移除 (2026-10-08 用户裁定): 不需要 LLM 决策
            # "用之前的什么性质"——快检不过的子性质直接走递归分解,
            # 已证性质经 KB 自动参与(创建复用 + 默认前提烘焙)
            lv = getattr(node, "_last_validity", None)
            if lv:
                # 反例注入: cex_full_timeline 已在 cha_verify 生成端做
                # .sys 敏感集抽象(命名信号~百级), 可整体直接注入
                ctx["上一轮有效性失败反例"] = lv
            dec = self._decompose_or_fail(task, ctx, self_rollback=True)
            if dec is None:
                # decomposer 失败: BFS 语义下回滚自身(错误路径计数已前置)
                # 节点可能已被旧回滚语义删除 → 存活守卫
                n2 = st.nodes.get(task)
                if n2 is None:
                    return
                if n2.status != ps.PENDING:
                    self._rollback(task, "local")
                    setattr(n2, "_round_started", False)
                    continue
                continue

            node.strategy = dec["strategy"]
            # 遗留 assume 清扫 (N86 虚假闭合修复): 假设效力只属于本轮,
            # 不在本轮 items 里的旧假设(含兑现子树)摘除, 防止后续
            # with_assumes=True 全量烘焙未兑现假设造成虚假证毕
            try:
                pruned = st.prune_stale_assumes(
                    task, [a.get("formula")
                           for a in (dec.get("assumes") or [])])
                if pruned:
                    self.report["events"].append(
                        f"{task}: 清扫遗留 assume {pruned} 条(非本轮)")
            except Exception as _e:
                self.report["events"].append(
                    f"{task}: assume 清扫异常(忽略): {_e}")
            self.report["events"].append(
                f"round {st.round}: {task} -> {dec['strategy']} (bfs)")

            node.pending_subs = 0
            if not hasattr(node, "_rounds"):
                node._rounds = []
            subtasks = []
            bad = False
            for child in dec.get("children") or []:
                try:
                    r = st.add_property(task, child)
                except ps.ProofStateError as e:
                    msg = str(e)
                    if "祖先重复" in msg:
                        # 环: 子性质与分解链祖先同签名(回到自身的路径)
                        # → 反馈重新分解 (语义等价审查不在框架范围)
                        st.record_failure(task, "ITER_EXCEED",
                                          cause="ANCESTOR_CYCLE",
                                          evidence=msg,
                                          hint="出现了环: 子性质与分解链上"
                                               "祖先同签名(自我回归), 请换"
                                               "其它分解形状, 勿再提出该性质")
                    else:
                        st.record_failure(task, "ITER_EXCEED",
                                          cause="SIGNAL_PATH_ERROR",
                                          evidence=msg,
                                          hint="child 的 signals 路径必须是"
                                               "宿主模块的真实端口路径"
                                               "(io.xxx...)")
                        # 规范类错误不占 LLM 预算(同编译 refund 先例)
                        st.refund_attempt(task)
                    bad = True
                    break
                # 结论输入守卫 (2026-10-09 用户语义):
                # CONJUNCT 分解出的子性质, 结论是本模块 Input → 直接拒绝
                # (性质分解应把子性质放到 writer 模块视角, 不该放这里)
                if self._conclusion_input_guard(task, r["id"]):
                    st.record_failure(task, "ITER_EXCEED",
                        cause="CONCLUSION_IS_INPUT",
                        evidence=f"子性质结论信号在本模块是 Input(自由输入), "
                                 f"模块级验证必出反例——CONJUNCT 分解应把 "
                                 f"子性质放到 writer 模块视角提出",
                        hint="结论是本模块自由输入 → 若继续分解(CONJUNCT), "
                             "请把子性质 signals 登记到结论信号的驱动模块"
                             "(writer)视角; 或改用 ASSUME 在本模块约束输入")
                    bad = True
                    break
                if r.get("short_circuited"):
                    if r.get("short_circuit_reason") == "timeout":
                        # 等价性质超时上限: 该子结点难以兑现 → 反馈换方案,
                        # 且此次分解不算(退还父尝试计数, 2026-09-28 用户语义)
                        st.record_failure(task, "TIMEOUT",
                            cause="TIMEOUT_RETRY_EXCEEDED",
                            evidence=f"子性质 {child.get('formula', '')} 的"
                                     f"等价签名已超时 {ps.TIMEOUT_RETRY_MAX}"
                                     f" 次, 难以兑现",
                            hint="该子结点难以兑现, 请尝试其它分解方案"
                                 "(更换性质形状/换模块视角, 勿再提出同签名"
                                 "性质)")
                        st.refund_attempt(task)
                        bad = True
                    continue
                if not r.get("reused_from"):
                    subtasks.append((r["id"], "assert"))
                # 检测子性质是否放到了其它模块(战略提示的前提检查)
                try:
                    child_mod = next(iter(
                        (st.nodes[r["id"]].signals or {}).values()),
                        {}).get("module")
                    own_mod = node.derived.get("module") or \
                        self.prop_module(node)
                    if child_mod and own_mod and child_mod != own_mod:
                        node._tried_other_module = True
                except Exception:
                    pass
                setattr(st.nodes[r["id"]], "sub_owner", task)
            if not bad:
                for a in dec.get("assumes") or []:
                    try:
                        aid = st.add_assume(task, a)
                    except ps.ProofStateError as e:
                        st.record_failure(task, "ITER_EXCEED",
                                          cause="ASSUME_REJECTED",
                                          evidence=str(e))
                        bad = True
                        break
                    # ── assume 全局筛 (与 children 同等处理, 一致性保证) ──
                    # 假设须在真实系统(Tile+先验)下成立; FAIL = 不可兑现的
                    # 虚假假设(典型: 对环境行为的活跃性约定), 当场拒绝,
                    # 不挂树不进债——否则充分性检查会被强假设平凡通过,
                    # 债务螺旋反复生成同式假设 (run_20260928_142536 实证)
                    did = st.nodes[aid].discharged_by
                    d = st.nodes[did]
                    if d.status == ps.IC3_PROVEN:
                        continue              # KB 复用: 已兑现
                    if d.status == ps.TIMEOUT_UNPROVED:
                        # 等价签名超时上限: 该假设难以兑现 → 反馈换方案,
                        # 此次分解不算(退还父尝试计数)
                        st.record_failure(task, "TIMEOUT",
                            cause="TIMEOUT_RETRY_EXCEEDED",
                            evidence=f"假设 {a.get('formula', '')} 的等价"
                                     f"签名已超时 {ps.TIMEOUT_RETRY_MAX} 次,"
                                     f"难以兑现",
                            hint="该假设难以兑现, 请尝试其它分解方案"
                                 "(换性质形状/停滞前件/换模块视角)")
                        st.refund_attempt(task)
                        bad = True
                        break
                    if d.status == ps.BMC_FAILED:
                        st.record_failure(task, "VIOLATED",
                                          cause="ASSUME_NEG_KB",
                                          evidence=f"assume 命中反KB: "
                                                   f"{a.get('formula', '')}")
                        bad = True
                        break
                    raw = self.run_bmc_filter(did)
                    self._record_outcome(did, "global_bmc", raw, "Tile")
                    if self._framework_abort(raw):
                        return
                    if raw.get("verdict") != "PASS":
                        st.record_failure(task, "VIOLATED",
                            cause="ASSUME_FALSIFIED",
                            evidence=f"假设在 Tile(真实系统+先验)下不成立: "
                                     f"{a.get('formula', '')} | "
                                     f"{str(raw.get('detail', ''))[:100]}",
                            hint="假设不可为对环境行为的活跃性约定(如"
                                 "'环境最终发请求'); 应改用带停滞前件的"
                                 "假设(G v -> F r)或分解为子性质; 真环境"
                                 "契约应进 priors 而非 assume")
                        bad = True
                        break
                    st.mark(did, ps.BMC_FILTERED)
                    # 快检: 模块级即时兑现(当场还债, 无螺旋)
                    raw2 = self.run_module_ic3(did)
                    if d.status == ps.IC3_PROVEN or \
                            raw2.get("verdict") == "PASS":
                        if d.status != ps.IC3_PROVEN:
                            st.mark(did, ps.IC3_PROVEN)
                        self._promote_ancestors(did)
                        self._settle(did)
                        continue
                    setattr(d, "sub_owner", task)
            if bad:
                # 入树原子性错误: 回滚自身, 原位重试(计数已前置)
                self._rollback(task, "local")
                continue

            node._round_started = True
            node.pending_subs = len(subtasks)
            # --- 全局筛选 + 全深度即时快检 ---
            to_verify = []                  # 未证毕 → 候选
            round_syntax_err = False
            for nid, kind in subtasks:
                n2 = st.nodes[nid]
                if n2.status in (ps.IC3_PROVEN, ps.SKIPPED, ps.BMC_FAILED):
                    self._settle(nid)
                    continue
                raw = self.run_bmc_filter(nid)
                self._record_outcome(nid, "global_bmc", raw, "Tile")
                if self._framework_abort(raw):
                    return
                if self._note_syntax_error(task, raw):
                    round_syntax_err = True
                if raw.get("verdict") != "PASS":
                    self._fail_quiet(nid, raw)
                    self._settle(nid)
                    continue
                st.mark(nid, ps.BMC_FILTERED)
                setattr(n2, "_sub_kind", kind)
                raw2 = self.run_module_ic3(nid)     # 快检: BMC+多落点+IC3
                if n2.status == ps.IC3_PROVEN or \
                        (raw2.get("verdict") == "PASS" and
                         not getattr(n2, "assumes", None)):
                    if n2.status != ps.IC3_PROVEN:
                        st.mark(nid, ps.IC3_PROVEN)
                    self._promote_ancestors(nid)
                    self._settle(nid)
                    continue                          # 快检证毕, 已入 KB
                # 快检不过 → 直接递归分解 (候选池已移除)
                to_verify.append(nid)

            # --- 有效性检查: 按策略分流 ---
            # ASSUME → 检查二(模块级充分性): 原子模块设计行为 + 本轮
            #   assumes ⊢ 目标。assume 信号生而对齐目标模块 Input 端口
            #   (add_assume 门禁保证), 与目标信号同视图物化, 无需改写;
            #   本模块先验照常烘焙, 它模块先验不参与(assume 组须自含)。
            # CONJUNCT → 检查一(空设计蕴含): 前提=候选+KB+先验 纯逻辑拼合。
            if node.strategy == "ASSUME" and self._prune_falsified(task) \
                    and getattr(node, "assumes", None):
                home = node.derived.get("module") or self.prop_module(node)
                try:
                    decls, formulas = self._materialize(
                        self._node_sources(node, with_assumes=True))
                except SignalGenError as e:
                    self._record_outcome(task, "assume_validity@" + home,
                        {"verdict": "ERROR",
                         "detail": f"信号生成错误: {e}"}, home)
                    self._fail_quiet(task,
                        {"verdict": "ERROR",
                         "detail": f"信号生成错误: {e}"})
                    continue
                # KB 默认前提 (2026-10-06 补检查二): 相关且可见的已证定理
                # 并入有效性前提——与 run_module_ic3 同一覆盖面
                kb_srcs = self._kb_premises_for(node, home)
                kb_kids = []
                if kb_srcs:
                    try:
                        n_own = len(formulas)
                        decls, formulas = self._materialize(
                            self._node_sources(node, with_assumes=True)
                            + [src[:2] for src in kb_srcs])
                        kb_used = formulas[n_own:]
                        kb_kids = [src[2] for src in kb_srcs]
                    except SignalGenError:
                        kb_used = []
                else:
                    kb_used = []
                kb_tag = f" [KB:{','.join(kb_kids)}]" if kb_kids else ""
                common = dict(module=home, signals=decls,
                              assert_formula=formulas[0],
                              assumes=formulas[1:],
                              priors_by_module=self.priors_by_module)
                valid = self.verifier(mode="bmc", **common)
                if kb_tag and isinstance(valid, dict):
                    valid = dict(valid)
                    valid["detail"] = str(valid.get("detail", "")) + kb_tag
                self._record_outcome(task, "assume_validity@" + home,
                                      valid, home)
                if valid.get("verdict") == "PASS":
                    valid = self.verifier(mode="ic3", **common)
                    if kb_tag and isinstance(valid, dict):
                        valid = dict(valid)
                        valid["detail"] = str(valid.get("detail", "")) + kb_tag
                    self._record_outcome(task, "assume_validity@" + home,
                                          valid, home)
            else:
                premise_srcs = [(st.nodes[nid].formula,
                                 st.nodes[nid].signals)
                                for nid in to_verify]
                for e in st.kb.entries:
                    premise_srcs.append((e.formula_raw or e.formula,
                                         e.signals))
                for m, xs in self.priors.items():
                    for x in xs:
                        premise_srcs.append((x["formula"], x["signals"]))
                valid = self._validity(task, premise_srcs)
            self._record_outcome(task, "implication", valid,
                                 node.derived.get("module") or
                                 self.prop_module(node))
            if self._framework_abort(valid):
                return
            if valid.get("verdict") == "PASS":
                # 蕴含先行验证落实 (2026-10-06): 置标志供升级守卫检查
                # (不用 MOD_PROVEN 状态——会扰乱 _settle 的 pending_subs 记账)
                node._implication_passed = True
                # 有效性通过 → assume 兑现节点统一压栈(开始还债)
                for a_id in (node.assumes or []):
                    dis_id = st.nodes[a_id].discharged_by \
                        if st.nodes[a_id].discharged_by in st.nodes else None
                    if dis_id and st.nodes[dis_id].status == ps.PENDING \
                            and dis_id not in st.stack:
                        st.stack.append(dis_id)
                # 压栈: 置信度序(逆序压栈)
                for nid in reversed(to_verify):
                    st.stack.append(nid)
                if not round_syntax_err:
                    self._rtl_errors = []   # 连续语义: 成功轮清零
                return
            # --- 有效性工具侧错误(非语义失败): 退还预算, 工具反馈重试 ---
            # ERROR(方法发射/编译/模板缺陷)不是 LLM 分解质量问题,
            # 不记 VALIDITY_FAIL, 不消耗回滚额度
            if valid.get("verdict") == "ERROR":
                self.st.refund_attempt(task)
                sub = valid.get("subtype") or ""
                kind = ("编译/公式生成错误" if sub in ("COMPILE", "SYNTAX")
                        else "工具侧错误")
                self.report["events"].append(
                    "{}: 有效性检查{}({}), 已退还额度, 反馈修正"
                    .format(task, kind, str(sub or
                              valid.get("detail", ""))[:60]))
                node._last_validity = {
                    "verdict": "ERROR",
                    "subtype": sub,
                    "detail": ("有效性检查{}(非语义失败, 须修正公式/环境"
                               "后重试): ".format(kind)
                               + str(valid.get("detail", ""))[:200]),
                    "cex_timeline": [], "cex_full_timeline": []}
                fb = critique({
                    "node": {"id": task, "formula": node.formula,
                             "nl": node.nl,
                             "assert_kind": node.assert_kind},
                    "strategy": node.strategy,
                    "cause": "VALIDITY_TOOL_ERROR",
                    "raw_result": dict(node._last_validity),
                    "history": [vars(f) for f in st.failures
                                if f.node == task][-3:],
                    "obligation_reference": self._obligation_ref(node),
                })
                self.report["events"].append(
                    "{}: 工具错误反馈: {}".format(
                        task, str(fb.get("hint", ""))[:80]))
                setattr(node, "_round_started", False)
                return
            # --- 有效性失败: 反馈 + 预算 + 原位重做 ---
            # 反例时序(cex_timeline)保留进反馈——蕴含反例中各信号取值
            # 是 LLM 修正前提组合的关键依据, 不可只传 verdict+detail
            node._last_validity = {
                "verdict": valid.get("verdict"),
                "detail": valid.get("detail", ""),
                "cex_timeline": valid.get("cex_timeline") or [],
                "cex_full_timeline": valid.get("cex_full_timeline") or [],
            }
            fb = critique({
                "node": {"id": task, "formula": node.formula,
                         "nl": node.nl, "assert_kind": node.assert_kind},
                "strategy": node.strategy,
                "cause": "VALIDITY_FAIL",
                "raw_result": dict(node._last_validity),
                "本轮被筛性质(次要参考, 优先分析有效性反例)": \
                    getattr(node, "_round_filter_errors", []),
                "history": [vars(f) for f in st.failures
                            if f.node == task][-3:],
                "obligation_reference": self._obligation_ref(node),
            })
            node._round_filter_errors = []      # 已消费, 防跨轮堆积
            self._record_round(task, [], [], [])
            st.record_failure(task, "VIOLATED", cause="VALIDITY_FAIL",
                              evidence=fb.get("evidence", ""),
                              hint=fb.get("hint", ""))
            if node.fail_count >= ps._rollback_allowed(node.depth):
                st.mark(task, ps.SKIPPED)
                if st.stack and st.stack[-1] == task:
                    st.stack.pop()
                self._settle(task)
                self._round_end_check(task)
                return
            self._rollback(task, "local")
            setattr(node, "_round_started", False)

    def _decompose(self, task):
        st = self.st
        node = st.nodes[task]

        # 败者终态防御: 全局证伪/超时/跳过的节点不进入分解
        # (历史 bug: 败者经栈重返分解, mark(SKIPPED) 触发非法迁移崩溃)
        if node.status in (ps.BMC_FAILED, ps.SKIPPED, ps.TIMEOUT_UNPROVED):
            if st.stack and st.stack[-1] == task:
                st.stack.pop()
            self._settle(task)
            self._round_end_check(task)
            return

        # 蕴含已先行验证（MOD_PROVEN）且全部子节点终态 → 直接升级
        # (2026-10-06 守卫: status 必须 MOD_PROVEN——只信注释不检查会在
        #  蕴含未过时静默假闭合)
        if node.strategy == "CONJUNCT" and node.children and \
                (node.status == ps.MOD_PROVEN
                 or getattr(node, "_implication_passed", False)) and all(
                st.nodes[c].status in (ps.IC3_PROVEN, ps.TIMEOUT_UNPROVED)
                for c in node.children):
            # 弃权连坐已移除 (2026-10-09 用户裁定): 前提正确性由
            # KB 入库门禁+默认前提自动保证——通过→入KB→可作前提;
            # 未通过→不入KB→不可能成为前提。N86 修复靠清扫。
            st.mark(task, ps.IC3_PROVEN)
            if st.stack and st.stack[-1] == task:
                st.stack.pop()
            self._promote_ancestors(task)
            return
        if SEARCH_MODE == "bfs":
            return self._decompose_bfs(task)
        st.round += 1                        # DFS: 一次调用一轮
        self.report["rounds"] = st.round
        ctx = self._build_ctx(task)
        dec = self._decompose_or_fail(task, ctx)
        if dec is None:
            return

        node.strategy = dec["strategy"]
        # 遗留 assume 清扫 (同 BFS 路径, N86 虚假闭合修复)
        try:
            pruned = st.prune_stale_assumes(
                task, [a.get("formula")
                       for a in (dec.get("assumes") or [])])
            if pruned:
                self.report["events"].append(
                    f"{task}: 清扫遗留 assume {pruned} 条(非本轮)")
        except Exception as _e:
            self.report["events"].append(
                f"{task}: assume 清扫异常(忽略): {_e}")
        self.report["events"].append(
            f"round {st.round}: {task} -> {dec['strategy']}")

        # ===== 批处理新流程 =====
        node.pending_subs = 0            # 重置本轮计数(上一轮残留)
        # 上一轮结果保留在 _rounds(不因回滚丢失, 供下一轮上下文使用)
        if not hasattr(node, "_rounds"):
            node._rounds = []
        # 1) children+assumes 全部入树(原子性错误当场拦截)
        # 2) 逐条 Tile 全局 BMC 筛选: FAIL 筛掉(反馈留到轮末)
        # 3) 通过者入任务: child→模块IC3 / assume→discharge(递归同流程)
        # 4) 本轮全部有结果后 → 空设计有效性(前提=通过者+全部KB+先验)
        #    失败 → 本轮全部失败信息+通过清单 合并反馈重分解
        #    通过 → 父节点模块 IC3 定案 → children 入下一层分解
        subtasks = []                     # (节点id, kind)
        for child in dec.get("children") or []:
            try:
                r = st.add_property(task, child)
            except ps.ProofStateError as e:
                st.record_failure(task, "ITER_EXCEED",
                                  cause="SIGNAL_PATH_ERROR", evidence=str(e),
                                  hint="child 的 signals 路径必须是宿主模块"
                                       "的真实端口路径(io.xxx...)")
                st.refund_attempt(task)   # 规范类错误不占 LLM 预算
                self._rollback_after_fail(task, "local")
                return
            if r.get("short_circuited"):
                if r.get("short_circuit_reason") == "timeout":
                    # DFS 路径同语义: 超时上限子结点 → 反馈+退还尝试
                    st.record_failure(task, "TIMEOUT",
                        cause="TIMEOUT_RETRY_EXCEEDED",
                        evidence=f"子性质 {child.get('formula', '')} 的等价"
                                 f"签名已超时 {ps.TIMEOUT_RETRY_MAX} 次, "
                                 f"难以兑现",
                        hint="该子结点难以兑现, 请尝试其它分解方案")
                    st.refund_attempt(task)
                    self._rollback_after_fail(task, "local")
                    return
                continue                  # 反KB命中: 已记失败, 轮末反馈
            if not r.get("reused_from"):
                subtasks.append((r["id"], "assert"))
            setattr(st.nodes[r["id"]], "sub_owner", task)
        for a in dec.get("assumes") or []:
            try:
                aid = st.add_assume(task, a)
                did = st.nodes[aid].discharged_by
                subtasks.append((did, "discharge"))
                setattr(st.nodes[did], "sub_owner", task)
            except ps.ProofStateError as e:
                st.record_failure(task, "ITER_EXCEED",
                                  cause="ASSUME_REJECTED", evidence=str(e))
                self._rollback_after_fail(task, "local")
                return

        # 尝试计数已在分解调用前完成(前置), 此处无需重复

        if not subtasks:
            self._round_end_check(task)   # 全部复用/短路: 直接收敛
            return

        setattr(node, "_round_started", True)   # 标记本轮开始, 主循环据此做轮末

        st.nodes[task].pending_subs = len(subtasks)
        # 逐条 BMC 筛选(按 agent 给出的置信度顺序)
        to_verify = []                          # 保持置信度序
        for nid, kind in subtasks:
            if st.nodes[nid].status in (ps.IC3_PROVEN, ps.SKIPPED,
                                       ps.BMC_FAILED):
                self._settle(nid)
                continue
            raw = self.run_bmc_filter(nid)
            self._record_outcome(nid, "global_bmc", raw, "Tile")
            if self._framework_abort(raw):
                return
            if raw.get("verdict") != "PASS":
                self._fail_quiet(nid, raw)      # 筛掉, 反馈留到轮末
                self._settle(nid)
                continue
            st.mark(nid, ps.BMC_FILTERED)
            setattr(st.nodes[nid], "_sub_kind", kind)
            to_verify.append(nid)
        # 入任务栈: 逆序压栈 → 栈顶为置信度最高者, 验证顺序 = 置信度递减
        for nid in reversed(to_verify):
            st.stack.append(nid)
        self._round_end_check(task)

    def _handle_bmc(self, node_id, raw):
        st = self.st
        v = raw.get("verdict")
        if v == "PASS":
            st.mark(node_id, ps.BMC_FILTERED)   # 留栈, 下一轮模块 IC3
        elif v == "FAIL":
            cause = ("CONTRADICT_ASSUME"
                     if st.nodes[node_id].strategy == "ASSUME"
                     else "BAD_DECOMP")
            level = self._fail(node_id, raw, cause)
            self._rollback_after_fail(node_id, level)
        else:                                    # ERROR（编译/语法/工具）
            if self._framework_abort(raw):
                return
            subtype = raw.get("subtype", "")
            cause = {"COMPILE": "COMPILE_ERROR",
                     "SYNTAX": "SYNTAX_ERROR"}.get(subtype, "TOOL_ERROR")
            outcome = "ITER_EXCEED" if cause in ("COMPILE_ERROR",
                                                 "SYNTAX_ERROR") else "TIMEOUT"
            if cause in ("COMPILE_ERROR", "SYNTAX_ERROR"):
                level = self._fail(node_id, raw, cause)   # critic 转写
            else:
                level = st.record_failure(node_id, outcome, cause,
                                          evidence=raw.get("detail", ""))
            self._rollback_after_fail(node_id, level)

    def _handle_ic3(self, node_id, raw):
        st = self.st
        if node_id not in st.nodes:       # 处理期间被轮末回滚删除
            return
        node = st.nodes[node_id]
        v = raw.get("verdict")
        if v == "PASS":
            if node.assumes:
                st.mark(node_id, ps.MOD_PROVEN)   # 等兑现（已在栈上）
                # 兑现可能早已完成（DFS 顺序）→ 立即尝试自提升
                if all(st.nodes[st.nodes[a].discharged_by].status
                       == ps.IC3_PROVEN for a in node.assumes):
                    st.mark(node_id, ps.IC3_PROVEN)
                    if st.stack and st.stack[-1] == node_id:
                        st.stack.pop()
                    self._promote_ancestors(node_id)
            else:
                if node.status != ps.IC3_PROVEN:  # 多落点可能已标记
                    st.mark(node_id, ps.IC3_PROVEN)
                if st.stack and st.stack[-1] == node_id:
                    st.stack.pop()
                self._promote_ancestors(node_id)
        elif v == "FAIL":
            # 全局BMC已通过(全局筛选阶段保证): 模块级卡住(模块BMC/IC3/
            # 多落点改写全败)→ 不回滚不烧critic, 静默记账, 该性质转
            # PENDING 原位重入队递归分解
            detail = raw.get("detail", "")
            alt = getattr(node, "_alt_fail_detail", "")
            ev = (f"全局BMC已通过但模块级不可直接证明: {detail}"
                  + (f" | 多落点改写: {alt}" if alt else "")
                  + " ——该性质非简单可处理, 转为递归分解:"
                    "请在信号的 writer 模块视角下改写本性质或补充"
                    "分解(非宿主模块信号需换成该模块可见的等价线)")
            # MODULE_STUCK: 全局BMC已通过, 模块级(含多落点)卡住——
            # 不是证伪, 不进反 KB, 重入队递归分解 (2026-09-29 用户语义)
            st.record_failure(node_id, "MODULE_STUCK",
                              cause="QUICK_VERIFY_FAIL", evidence=ev)
            st.mark(node_id, ps.PENDING)   # 留在原位(置信度序),
            return                         # 阶段1 立即递归分解
        else:
            st.mark(node_id, ps.TIMEOUT_UNPROVED)
            self._promote_ancestors(node_id)
            if st.stack and st.stack[-1] == node_id:
                st.stack.pop()

    def _read_source(self, src: str, cap: int = 600) -> str:
        """读模块源码（超长截断）。src 相对 riscv-mini 根。"""
        p = Path(__file__).resolve().parents[2] / src if src else None
        if not p or not p.exists():
            return f"（源码不可读: {src}）"
        text = p.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        if len(lines) > cap:
            return "\n".join(lines[:cap]) + f"\n// ...（截断, 共 {len(lines)} 行）"
        return text

    def _assume_alt_modules(self, node):
        """assume 信号的全部可表达模块(除原模块), writer 优先。"""
        cands = set()
        for s in (node.signals or {}).values():
            mod = s["module"]
            for c in self.h.connections:
                a, b = c.frm.split(".", 1)[0], c.to.split(".", 1)[0]
                if a == mod: cands.add(b)
                if b == mod: cands.add(a)
        cands.discard(mod)
        # writer 优先
        writers = set(self._signal_writers(node).values())
        ordered = sorted(cands, key=lambda m: (m not in writers, m))
        return ordered

    def _rewrite_signals_for(self, node, to_mod):
        """assume 信号改写到 to_mod 视角; 任一失败返回 (None, 原因)。"""
        from_mod = next(iter((node.signals or {}).values()))["module"]
        out = {}
        for alias, s in (node.signals or {}).items():
            if s.get("expr"):
                new = rewrite_expr(s["expr"], from_mod, to_mod,
                                   self.h, self.reader)
                if new is None:
                    return None, (f"信号{alias}(expr {s['expr']}"
                                  f"@{from_mod})不可改写到{to_mod}视角")
                out[alias] = {"module": to_mod, "expr": new,
                              "port": "expr:" + new}
            else:
                new = rewrite_path(s["port"], from_mod, to_mod, self.h)
                if new is None:
                    return None, (f"信号{alias}({s['port']}@{from_mod})"
                                  f"与{to_mod}无层次连接")
                out[alias] = {"module": to_mod, "port": new}
        return out, ""

    def _obligation_ref(self, node) -> list:
        """失败性质的通路族义务标注(仅 name/obligation/note, 无通路原文)。
        引导不可用/无缓存返回 []。"""
        try:
            if not hasattr(self, "_pg"):
                from path_guidance import PathGuidance
                self._pg = PathGuidance()
            if not self._pg.available():
                return []
            module = node.derived.get("module") or self.prop_module(node)
            r = self._pg.guidance(module, node.formula, node.signals)
            fams = (r.get('classified') or {}).get('families') or []
            return [{'family': f.get('name'),
                     'obligation': f.get('obligation'),
                     'note': f.get('note')}
                    for f in fams if f.get('note')]
        except Exception:
            return []

    def _landing_hint(self, node):
        """gate 驱动反查: 性质输入信号共同的驱动模块(静态确定性),
        无/异常返回 None。"""
        try:
            if not hasattr(self, "_pg"):
                from path_guidance import PathGuidance
                self._pg = PathGuidance()
            if not self._pg.available():
                return None
            module = node.derived.get("module") or self.prop_module(node)
            drivers = set()
            for s in (node.signals or {}).values():
                port = s.get("port")
                if not port or port.startswith("expr:"):
                    continue
                lp = self._pg._local_ports(module)
                if lp.get(port.replace('.', '_')) != 'input':
                    continue
                drivers.add(self._pg._drivers_module(
                    port.replace('.', '_'), module))
            drivers.discard(None)
            drivers.discard('__env__')
            drivers.discard('__pruned__')
            if len(drivers) == 1:
                inst = next(iter(drivers))
                t = self._pg.ng.inst2type.get(inst, '')
                if t.startswith('AG') and t.endswith('Prop'):
                    return t[2:-4]
        except Exception:
            pass
        return None

    def _try_alternate_modules(self, node_id):
        """assume 兑现在原模块失败后, 逐候选模块顺序尝试验证。
        成功 → 标记 proven_at 并返回 True; 全败返回 False。
        全路径日志进 events + outcomes 便于诊断。"""
        st = self.st
        node = st.nodes[node_id]
        cands = self._assume_alt_modules(node)
        hint = self._landing_hint(node)
        if hint and hint in cands:
            cands = [hint] + [c for c in cands if c != hint]
            self.report["events"].append(
                f"{node_id}: gate驱动者 {hint} 排多落点首位")
        elif hint and hint not in cands:
            self.report["events"].append(
                f"{node_id}: gate驱动者 {hint} 不在连接候选中(忽略)")
        self.report["events"].append(
            f"{node_id}: 多落点尝试, 候选={cands}")
        self._record_outcome(node_id, "alt_modules", {
            "verdict": "INFO",
            "detail": f"候选={cands}"}, node.derived.get("module"))
        reasons = []
        for cand in cands:
            sigs, why = self._rewrite_signals_for(node, cand)
            if sigs is None:
                self.report["events"].append(
                    f"{node_id}: 候选{cand} 信号改写失败: {why}")
                self._record_outcome(node_id, "alt_rewrite@" + cand, {
                    "verdict": "INFO", "detail": why}, cand)
                reasons.append(why)
                continue
            decls = [(a, ps.ProofState.signal_path(s), i + 1)
                     for i, (a, s) in enumerate(sigs.items())]
            common = dict(module=cand, signals=decls,
                          assert_formula=node.formula, assumes=[],
                          priors_by_module=self.priors_by_module)
            raw = self.verifier(mode="bmc", **common)
            self._record_outcome(node_id, "alt_bmc@" + cand, raw, cand)
            if self._framework_abort(raw): return False
            if raw.get("verdict") != "PASS":
                continue
            # bmc_first (2026-10-09): 多落点也跳过 IC3, BMC 过即视为通过
            if VERIFY_MODE == "bmc_first":
                node.proven_at = cand
                if node.status != ps.IC3_PROVEN:
                    st.mark(node_id, ps.BMC_FILTERED)
                self.report["events"].append(
                    f"{node_id}: 多落点 BMC 过@{cand} (bmc_first)")
                self._settle(node_id)
                return True
            raw = self.verifier(mode="ic3", **common)
            self._record_outcome(node_id, "alt_ic3@" + cand, raw, cand)
            if self._framework_abort(raw): return False
            if raw.get("verdict") == "PASS":
                node.proven_at = cand
                # 不改写信号视角: 保留当前子模块的原始性质(防重复——
                # 多落点证毕只是证据, 性质仍以原视角参与后续/KB)
                if node.status != ps.IC3_PROVEN:
                    st.mark(node_id, ps.IC3_PROVEN)
                self.report["events"].append(
                    f"{node_id}: assume 兑现于候选模块 {cand} 证毕"
                    f"(原模块失败)")
                self._settle(node_id)
                return True
        node._alt_fail_detail = "; ".join(reasons)
        return False

    def _alt_attempts_for(self, node_id):
        """该节点的多落点尝试记录(供 critic 上下文)"""
        alts = []
        try:
            for line in open(self.run_dir / "outcomes.jsonl",
                             encoding="utf-8"):
                r = json.loads(line)
                if (r.get("node") == node_id
                        and r.get("phase", "").startswith("alt_")
                        and r.get("verdict") != "INFO"):
                    alts.append({
                        "candidate": r.get("module") or r.get("phase","").split("@")[-1],
                        "phase": r.get("phase"),
                        "verdict": r.get("verdict"),
                        "detail": (r.get("detail") or "")[:80]})
        except Exception:
            pass
        return alts

    def _signal_writers(self, node) -> Dict:
        """节点各信号的驱动模块（registry 方向信息）"""
        out = {}
        for local, s in (node.signals or {}).items():
            wid = ps.wire_id_of(s, self.h)
            e = self.st.registry.entries.get(wid)
            out[local] = (e.writer if e else None) or "未知"
        return out

    def _known_signals(self, node_id) -> List:
        """已声明的信号清单——agent 应复用而非另起新别名。
        来源: 先验 / KB 定理 / 父性质 / 同轮兄弟。"""
        st = self.st
        node = st.nodes[node_id]
        out, seen = [], set()

        def add(alias, module, path, source):
            key = (alias, module, path)
            if key in seen or len(out) >= 30:
                return
            seen.add(key)
            out.append({"alias": alias, "module": module, "path": path})

        for m, p in self.priors_by_module.items():
            for alias, path, _n in p.get("signals", []):
                add(alias, m, path, "prior")
        for e in st.kb.entries:
            for alias, s in (e.signals or {}).items():
                add(alias, s.get("module", "?"),
                    s.get("port") or s.get("expr") or "?", "kb定理")
        for alias, s in (node.signals or {}).items():
            add(alias, s["module"],
                s.get("port") or s.get("expr") or "?", "父性质")
        owner = getattr(node, "sub_owner", None) or node.parent
        if owner and owner in st.nodes:
            for cid in st.nodes[owner].children + st.nodes[owner].assumes:
                c = st.nodes.get(cid)
                if not c:
                    continue
                for alias, s in (c.signals or {}).items():
                    add(alias, s["module"],
                        s.get("port") or s.get("expr") or "?", "同轮性质")
        return out

    def _lineage(self, node_id) -> Dict:
        """谱系: 产生该节点的分解上下文（降层再分解时可用本轮信息）。
        - parent: 父性质与其策略
        - siblings: 同轮其它子性质/假设兑现的结果
        - origin: discharge 则注明源 assume"""
        st = self.st
        node = st.nodes[node_id]
    # 向上找分解者: discharge→assume→owner; child→owner
        owner = getattr(node, "sub_owner", None)
        info = {}
        if node.parent and node.parent in st.nodes:
            p = st.nodes[node.parent]
            info["parent"] = {"id": p.id, "formula": p.formula,
                              "strategy": p.strategy}
            if p.kind == "assume":            # 经由 assume 的 discharge
                info["origin_assume"] = p.formula
                gp = p.parent
                if gp and gp in st.nodes:
                    g = st.nodes[gp]
                    info["parent"] = {"id": g.id, "formula": g.formula,
                                      "strategy": g.strategy}
                    owner = gp
        sibs = []
        if owner and owner in st.nodes:
            o = st.nodes[owner]
            for cid in o.children + o.assumes:
                c = st.nodes.get(cid)
                if not c or c.id == node_id:
                    continue
                sib = {"formula": c.formula, "kind": c.kind,
                       "status": c.status}
                if c.kind == "assume" and c.discharged_by in st.nodes:
                    sib["discharge_status"] = st.nodes[
                        c.discharged_by].status
                sibs.append(sib)
        info["siblings"] = sibs
        return info

    def _note_syntax_error(self, task, raw) -> bool:
        """编译错误轮: ①退还该轮分解额度(可能是压缩问题非分解问题)
        ②收集错误样本。连续多轮(>=4)才触发重压缩; 成功轮清零。
        返回是否语法错误。"""
        try:
            if raw.get("verdict") != "ERROR":
                return False
            det = raw.get("detail", "") or ""
            if "编译失败" not in det and "not found" not in det:
                return False
            self.st.refund_attempt(task)
            ids = re.findall(r"not found: value (\S+)", det)
            self._rtl_errors.extend(
                "表达式引用了不存在的信号 {}: 请在摘要中给出该处正确的"
                "信号/状态名(源码逐字)".format(i) for i in ids)
            self.report["events"].append(
                "{}: 编译错误(可能为压缩问题), 已退还本轮额度".format(task))
            return True
        except Exception:
            return False

    def _rtl_text(self, node) -> dict:
        """RTL 压缩摘要 → __text__ 形式; 失败返回 None(降级用源码)。
        语法错误连续 >=4 时以出错表达式为反馈重压缩。"""
        try:
            from rtl_compress import get_digest, invalidate
            root = self.st.nodes.get("N1") or node
            sources = {}
            for m in self.h.modules.values():
                s = self._read_source(m.src, cap=400)
                if s:
                    sources[m.name] = s
            errs = self._rtl_errors if len(self._rtl_errors) >= 4 else None
            if errs:
                invalidate(root.formula, sources)
                self._rtl_errors = []
            r = get_digest(root.formula, sources, error_examples=errs)
            self._rtl_key = r.get("key")
            return {"压缩RTL摘要(性质相关, 名字已校验)":
                    r["digest"]}
        except Exception:
            return None

    def _module_brief(self, node) -> Dict:
        """decomposer 的设计上下文。

        json_part: 结构化摘要（归属/模块清单/连接表）
        text_part: 模块源码——经 __text__ 通道以真实换行传递,
                   不被 JSON 转义压成单行（保留代码结构）。
        """
        module = node.derived.get("module") or self.prop_module(node)
        info = self.h.modules.get(module)
        conns = [{"from": c.frm, "to": c.to} for c in self.h.connections]

        total_cap = 1500
        own = self._read_source(info.src if info else "",
                                cap=min(600, total_cap))
        used = len(own.splitlines())
        others_meta = []
        text_part = {f"归属模块 {module} ({info.src if info else ''}) 源码":
                     own}
        for m in self.h.modules.values():
            if m.name == module:
                continue
            remaining = total_cap - used
            if remaining <= 50:
                others_meta.append({"name": m.name, "inst": m.inst,
                                    "source": "（预算用尽省略）"})
                continue
            s = self._read_source(m.src, cap=min(300, remaining))
            used += len(s.splitlines())
            others_meta.append({"name": m.name, "inst": m.inst,
                                "parent": m.parent})
            text_part[f"其它模块 {m.name} (inst={m.inst}) 源码"] = s

        json_part = {"module": module, "src": info.src if info else "",
                     "other_modules": others_meta,
                     "connections": conns,
                     "note": "各模块完整源码见下方文本区(真实换行)"}
        return {"json_part": json_part, "text_part": text_part}



def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    d = Dispatcher(argv[1], argv[2])
    report = d.run()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("conclusion") == "SUCCESS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
