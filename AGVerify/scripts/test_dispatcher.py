#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dispatcher 单元测试: mock cha_verify 与 decomposer/critic, 不跑 sbt/LLM"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agents"))

import dispatcher as dp
import test_proof_state as tp
import proof_state as ps
from classify_prop import DesignReader, Hierarchy


def setUpModule():
    """测试统一把 REPORT 指到临时目录, 不污染真实 results/;
    默认回归 DFS 模式(BFS 测试类内自行切换)。"""
    import tempfile
    dp.REPORT = Path(tempfile.mkdtemp())
    dp.SEARCH_MODE = "dfs"
    dp.VERIFY_MODE = "standard"
    ps.CONFIG["verify_mode"] = "standard"

HIER = {
    "modules": [
        {"name": "Tile"},
        {"name": "Datapath", "inst": "core", "parent": "Tile"},
        {"name": "ICache", "inst": "icache", "parent": "Tile"},
    ],
    "connections": [
        {"from": "Datapath.imem", "to": "ICache.io"},
    ],
}


class FakeReader(DesignReader):
    def port_direction(self, module, port):
        if module == "Datapath" and port.startswith(("imem",)):
            return "Output"
        if module == "ICache" and port.startswith("io"):
            return "Input"
        return None


def mk_dispatcher(verifier):
    d = Path(tempfile.mkdtemp())
    (d / "h.json").write_text(json.dumps(HIER), encoding="utf-8")
    (d / "p.json").write_text(json.dumps({
        "id": "P1", "formula": "G(req -> F resp)",
        "signals": {"req": {"module": "ICache", "port": "io.cpu.req.valid"},
                    "resp": {"module": "ICache", "port": "io.cpu.resp.valid"}}}
    ), encoding="utf-8")
    return dp.Dispatcher(str(d / "h.json"), str(d / "p.json"),
                         reader=FakeReader(), verifier=verifier)


def pass_v(*a, **k):
    return {"verdict": "PASS", "detail": ""}


def fail_v(*a, **k):
    return {"verdict": "FAIL", "detail": "violation @3"}


def conj_decision(**kw):
    return {"strategy": "CONJUNCT", "rationale": "r", "children": [
        {"id": "P1.1", "nl": "a", "formula": "G(req)",
         "signals": {"req": {"module": "ICache", "port": "io.cpu.req.valid"}}},
        {"id": "P1.2", "nl": "b", "formula": "F(resp)",
         "signals": {"resp": {"module": "ICache",
                              "port": "io.cpu.resp.valid"}}}]}


def conj2_decision(**kw):
    return {"strategy": "CONJUNCT", "rationale": "r", "children": [
        {"id": "D1", "nl": "a", "formula": "G(b)",
         "signals": {"b": {"module": "ICache", "port": "io.b"}}},
        {"id": "D2", "nl": "b", "formula": "F(b)",
         "signals": {"b": {"module": "ICache", "port": "io.b"}}}]}


def assume_decision(**kw):
    return {"strategy": "ASSUME", "rationale": "r", "assumes": [
        {"id": "A1", "nl": "env", "formula": "G(rdy)",
         "signals": {"rdy": {"module": "ICache",
                             "port": "io.nasti.ar.ready"}},
         "target_module": "ICache"}]}


class TestConjunctFlow(unittest.TestCase):
    def test_success(self):
        # 蕴含标志落地后需 2 轮: 轮1 证毕子节点+检查一, 轮2 入口提升
        with mock.patch.object(dp, "decompose",
                               side_effect=[conj_decision(),
                                            conj_decision()]), \
             mock.patch.object(dp, "critique") as mc, \
             mock.patch.object(dp, "cha_verify") as cv:
            cv.cha_verify = pass_v
            d = mk_dispatcher(pass_v)
            rep = d.run()
        self.assertEqual(rep["conclusion"], "SUCCESS")
        self.assertTrue(d.st.done())
        # 根经 CONJUNCT 分解, 两个 child 证毕, 根还需蕴含提升:
        # 当前实现: children PROVEN 后根仍 PENDING → 蕴含检查待实现?
        self.assertEqual(len(d.st.kb.entries) >= 2, True)


class TestAssumeFlow(unittest.TestCase):
    def test_mod_proven_then_discharge(self):
        # 全局 BMC PASS, 模块 IC3 PASS, 兑现 IC3 PASS
        calls = {"n": 0}

        def v(*a, **k):
            calls["n"] += 1
            return {"verdict": "PASS", "detail": ""}

        with mock.patch.object(dp, "decompose",
                               side_effect=[assume_decision(),
                                            conj2_decision(),
                                            conj2_decision()]), \
             mock.patch.object(dp, "critique"), \
             mock.patch.object(dp, "cha_verify") as cv:
            d = mk_dispatcher(v)
            rep = d.run()
        self.assertEqual(rep["conclusion"], "SUCCESS")
        # 兑现节点 PROVEN, 根被提升
        self.assertEqual(d.st.nodes[d.st.root].status, ps.IC3_PROVEN)


class TestFailureFlow(unittest.TestCase):
    def test_bmc_fail_rolls_back_and_retries(self):
        decisions = [conj_decision(), assume_decision(), conj2_decision(),
                     conj2_decision()]
        verbs = ["FAIL"]        # 第一次分解的 child BMC 失败

        def v(module, signals, assert_formula, assumes, mode, **k):
            if mode == "bmc" and verbs and verbs[0] == "FAIL":
                verbs.pop(0)
                return {"verdict": "FAIL", "detail": "violation @2"}
            return {"verdict": "PASS", "detail": ""}

        with mock.patch.object(dp, "decompose", side_effect=decisions), \
             mock.patch.object(dp, "critique",
                               side_effect=lambda ctx: {"evidence": "e",
                                                        "hint": "h"}), \
             mock.patch.object(dp, "cha_verify"):
            d = mk_dispatcher(v)
            rep = d.run()
        self.assertEqual(rep["conclusion"], "SUCCESS")
        self.assertEqual(len(d.st.failures), 1)   # 失败入账且保留
        self.assertTrue(d.st.done())


class TestQuickVerifyFailRequeue(unittest.TestCase):
    """多落点快速验证失败: discharge 节点不回滚不烧 critic,
    静默记账后转 PENDING 递归分解(用户语义)。
    场景复刻 run_20260907_125246 的 N11: (G !response) -> F ar.ready
    ——response 在 cpu 侧、ar.ready 在 nasti 侧, 整组改写必败。"""

    HIER_REAL = {
        "modules": [
            {"name": "Tile"},
            {"name": "Datapath", "inst": "core", "parent": "Tile"},
            {"name": "ICache", "inst": "icache", "parent": "Tile"},
            {"name": "MemArbiter", "inst": "arb", "parent": "Tile"},
        ],
        "connections": [
            {"from": "Datapath.io.icache", "to": "ICache.io.cpu"},
            {"from": "MemArbiter.io.icache", "to": "ICache.io.nasti"},
        ],
    }

    ASSUME = {
        "id": "A1", "nl": "停滞公平", "target_module": "ICache",
        "formula": "(G !response) -> F rdy",
        "signals": {
            "response": {"module": "ICache",
                         "port": "io.cpu.resp.valid"},
            "rdy": {"module": "ICache", "port": "io.nasti.ar.ready"}}}

    def test_requeue_and_recurse(self):
        d = Path(tempfile.mkdtemp())
        (d / "h.json").write_text(json.dumps(self.HIER_REAL),
                                  encoding="utf-8")
        (d / "p.json").write_text(json.dumps({
            "id": "P1", "formula": "F resp",
            "signals": {"resp": {"module": "ICache",
                                 "port": "io.cpu.resp.valid"}}}
        ), encoding="utf-8")

        state = {"module_bmc_failed": False}
        goals = []                      # 记录每次分解的目标公式
        order = []                      # 全局时序: 分解目标 vs 验证调用

        def v(module, signals, assert_formula, assumes, mode, **k):
            if k.get("run_at") == "Tile":     # 全局 BMC 筛选
                return {"verdict": "PASS", "detail": ""}
            if mode == "bmc" and not state["module_bmc_failed"]:
                state["module_bmc_failed"] = True
                order.append("A1_mod_fail")
                return {"verdict": "FAIL", "detail": "violation @3"}
            order.append(f"{mode}:{assert_formula}")
            return {"verdict": "PASS", "detail": ""}

        def dec(ctx):
            f = ctx["待验证性质(当前分解目标, node)"]["formula"]
            goals.append(f)
            order.append(f"decompose:{f}")
            if len(goals) == 1:               # 根: N11 同款 + 兄弟 assume
                return {"strategy": "ASSUME", "rationale": "r",
                        "assumes": [dict(self.ASSUME), {
                            "id": "A2", "nl": "简单", "target_module": "ICache",
                            "formula": "G cpuReq",
                            "signals": {"cpuReq": {
                                "module": "ICache",
                                "port": "io.cpu.req.valid"}}}]}
            return conj2_decision()           # 后续轮: 任意可证分解

        with mock.patch.object(dp, "decompose", side_effect=dec), \
             mock.patch.object(dp, "critique") as cr, \
             mock.patch.object(dp, "cha_verify"):
            disp = dp.Dispatcher(str(d / "h.json"), str(d / "p.json"),
                                 reader=FakeReader(), verifier=v)
            rep = disp.run()
        self.assertEqual(rep["conclusion"], "SUCCESS")
        # critic 不被模块级快速验证失败触发
        self.assertFalse(cr.called)
        # 第二轮分解目标 = 该性质本身(递归处理), 而非回滚根重分解
        self.assertEqual(goals[1], "(G !response) -> F rdy")
        # 置信度序保持: A1 失败后原位递归分解(先于兄弟 A2 的模块验证),
        # 轮末仍等全部终态
        i_fail = order.index("A1_mod_fail")
        i_re = order.index("decompose:(G !response) -> F rdy")
        i_a2 = order.index("ic3:G cpuReq")
        self.assertTrue(i_fail < i_re < i_a2)
        # 失败证据含具体改写失败信号(cpu 侧信号不可迁 MemArbiter)
        f = next(x for x in disp.st.failures
                 if x.cause == "QUICK_VERIFY_FAIL")
        self.assertIn("response", f.evidence)
        self.assertIn("MemArbiter", f.evidence)
        self.assertTrue(disp.st.done())


class TestChildModuleFailRequeue(unittest.TestCase):
    """child assert 模块级 FAIL(N9 场景): 同样重入队递归分解, 不回滚父轮"""

    def test_child_requeue(self):
        goals = []
        state = {"mod_fail": False}

        def v(module, signals, assert_formula, assumes, mode, **k):
            if k.get("run_at") == "Tile":
                return {"verdict": "PASS", "detail": ""}
            if mode == "bmc" and not state["mod_fail"]:
                state["mod_fail"] = True
                return {"verdict": "FAIL", "detail": "violation @3"}
            return {"verdict": "PASS", "detail": ""}

        def dec(ctx):
            goals.append(ctx["待验证性质(当前分解目标, node)"]["formula"])
            if len(goals) == 1:            # 根: CONJUNCT, child 模块级会失败
                return conj_decision()     # child: G(req) 与 F(resp)
            return conj2_decision()

        with mock.patch.object(dp, "decompose", side_effect=dec), \
             mock.patch.object(dp, "critique") as cr, \
             mock.patch.object(dp, "cha_verify"):
            d = mk_dispatcher(v)
            rep = d.run()
        self.assertEqual(rep["conclusion"], "SUCCESS")
        # 模块级 FAIL 的 child 被重入队递归分解(第二轮目标=该 child 公式)
        self.assertEqual(goals[1], "G(req)")
        self.assertFalse(cr.called)        # 不烧 critic, 不走回滚
        self.assertTrue(d.st.done())


class TestRoundFailSelfRollback(unittest.TestCase):
    """轮末全败: 回滚自身并原位重分解(不上溯父链/空轮连锁), N52 场景。
    失败预算独立计数, 耗尽才 SKIP。"""

    HIER_REAL = TestQuickVerifyFailRequeue.HIER_REAL

    def test_self_rollback_and_retry(self):
        d = Path(tempfile.mkdtemp())
        (d / "h.json").write_text(json.dumps(self.HIER_REAL),
                                  encoding="utf-8")
        (d / "p.json").write_text(json.dumps({
            "id": "P1", "formula": "F resp",
            "signals": {"resp": {"module": "ICache",
                                 "port": "io.cpu.resp.valid"}}}
        ), encoding="utf-8")

        goals = []
        valid = {"n": 0}
        state = {"icache_failed": False}

        def v(module, signals, assert_formula, assumes, mode, **k):
            if module == "Implication":            # 蕴含: 首轮 FAIL
                valid["n"] += 1
                return ({"verdict": "FAIL", "detail": "premises insufficient"}
                        if valid["n"] == 1 else
                        {"verdict": "PASS", "detail": ""})
            if assert_formula == "G(!rdy)":        # 首次分解的 child: 全局筛掉
                return {"verdict": "FAIL", "detail": "global cex @2"}
            if k.get("run_at") == "Tile":
                return {"verdict": "PASS", "detail": ""}
            if mode == "bmc" and module == "ICache" and not state["icache_failed"]:
                state["icache_failed"] = True      # 快速验证失败一次
                return {"verdict": "FAIL", "detail": "violation @3"}
            return {"verdict": "PASS", "detail": ""}

        def dec(ctx):
            goals.append(ctx["待验证性质(当前分解目标, node)"]["formula"])
            n = len(goals)
            if n == 1:                     # 根: 跨模块 assume(不可迁移)
                return {"strategy": "ASSUME", "rationale": "r",
                        "assumes": [{
                            "id": "A1", "nl": "停滞公平", "target_module": "ICache",
                            "formula": "(G !response) -> F rdy",
                            "signals": {
                                "response": {"module": "ICache",
                                             "port": "io.cpu.resp.valid"},
                                "rdy": {"module": "ICache",
                                        "port": "io.nasti.ar.ready"}}}]}
            if n == 2:                     # 首次分解: child 全局 FAIL
                return {"strategy": "CONJUNCT", "rationale": "r", "children": [
                    {"id": "C1", "nl": "x", "formula": "G(!rdy)",
                     "signals": {"rdy": {"module": "ICache",
                                         "port": "io.nasti.ar.ready"}}}]}
            return conj2_decision()        # 重试: 可证分解

        with mock.patch.object(dp, "decompose", side_effect=dec), \
             mock.patch.object(dp, "critique",
                               side_effect=lambda ctx: {"evidence": "e",
                                                        "hint": "h"}), \
             mock.patch.object(dp, "cha_verify"):
            disp = dp.Dispatcher(str(d / "h.json"), str(d / "p.json"),
                                 reader=FakeReader(), verifier=v)
            rep = disp.run()
        self.assertEqual(rep["conclusion"], "SUCCESS")
        # 轮2分解该性质, 其轮末全败 → 轮3仍分解该性质自身(非上溯根)
        self.assertEqual(goals[1], "(G !response) -> F rdy")
        self.assertEqual(goals[2], "(G !response) -> F rdy")
        self.assertTrue(disp.st.done())


class TestBFSMode(unittest.TestCase):
    """BFS 模式: 阶段A(全局筛+即时快检+有效性循环+候选池)
    阶段B(主循环阶段2承接验证, 递归继承 BFS)。"""

    HIER_REAL = TestQuickVerifyFailRequeue.HIER_REAL

    def _mk(self, v):
        d = Path(tempfile.mkdtemp())
        (d / "h.json").write_text(json.dumps(self.HIER_REAL),
                                  encoding="utf-8")
        (d / "p.json").write_text(json.dumps({
            "id": "P1", "formula": "F resp",
            "signals": {"resp": {"module": "ICache",
                                 "port": "io.cpu.resp.valid"}}}
        ), encoding="utf-8")
        return dp.Dispatcher(str(d / "h.json"), str(d / "p.json"),
                             reader=FakeReader(), verifier=v)

    def test_bfs_full_flow(self):
        dp.SEARCH_MODE = "bfs"
        try:
            goals = []
            state = {"valid": 0, "rdy_fail_left": 2}

            def v(module, signals, assert_formula, assumes, mode, **k):
                if module == "Implication":       # 有效性: 首次 FAIL 再 PASS
                    state["valid"] += 1
                    return ({"verdict": "FAIL", "detail": "premises insufficient"}
                            if state["valid"] == 1 else
                            {"verdict": "PASS", "detail": ""})
                if k.get("run_at") == "Tile":     # 全局筛
                    return {"verdict": "PASS", "detail": ""}
                if "rdy" in assert_formula and mode == "bmc" \
                        and state["rdy_fail_left"] > 0:
                    state["rdy_fail_left"] -= 1   # 两次快检失败→候选+递归
                    return {"verdict": "FAIL", "detail": "violation @3"}
                return {"verdict": "PASS", "detail": ""}

            def dec(ctx):
                f = ctx["待验证性质(当前分解目标, node)"]["formula"]
                goals.append(f)
                out = {}
                if f == "F resp":
                    return {"strategy": "CONJUNCT", "rationale": "r",
                            "children": [
                                {"id": "C1", "nl": "a", "formula": "G(a)",
                                 "signals": {"a": {"module": "ICache",
                                                   "port": "io.a"}}},
                                {"id": "C2", "nl": "b",
                                 "formula": "(G !resp) -> F rdy",
                                 "signals": {
                                     "resp": {"module": "ICache",
                                              "port": "io.cpu.resp.valid"},
                                     "rdy": {"module": "MemArbiter",
                                             "port": "io.icache.ar.ready"}}}]}
                return {**conj2_decision(), **out}

            with mock.patch.object(dp, "decompose", side_effect=dec), \
                 mock.patch.object(dp, "critique",
                                   side_effect=lambda c: {"evidence": "e",
                                                          "hint": "h"}), \
                 mock.patch.object(dp, "cha_verify"):
                disp = self._mk(v)
                rep = disp.run()
            self.assertEqual(rep["conclusion"], "SUCCESS")
            # 2) 有效性失败 → 根原位重做(轮2 仍是根公式)
            self.assertEqual(goals[1], "F resp")
            # 3) 候选池移除后: 无表态轮/物化轮, 流程更短直接闭合
            self.assertTrue(disp.st.done())
        finally:
            dp.SEARCH_MODE = "dfs"


class TestAssumeScreening(unittest.TestCase):
    """assume 全局筛(一致性): 假设在 Tile(真实系统+先验)下不成立 →
    当场拒绝, 不挂树不进债 (run_20260928_142536 债务螺旋的修复)。
    场景: 'F cpuReqValid' 类环境活跃性假设, idle 轨迹必然违反。"""

    def test_falsified_assume_rejected_at_creation(self):
        dp.SEARCH_MODE = "bfs"
        try:
            screen_calls = []

            def v(module, signals, assert_formula, assumes, mode, **k):
                if k.get("run_at") == "Tile":     # 全局筛
                    screen_calls.append(assert_formula)
                    if "cpuReq" in assert_formula:
                        return {"verdict": "FAIL", "detail": "idle 轨迹违反"}
                    return {"verdict": "PASS", "detail": ""}
                return {"verdict": "PASS", "detail": ""}

            bad_then_good = [
                # 第一轮: 带虚假环境活跃性假设的 ASSUME
                {"strategy": "ASSUME", "rationale": "r", "assumes": [
                    {"id": "A1", "nl": "环境最终发请求",
                     "formula": "F cpuReq",
                     "signals": {"cpuReq": {"module": "ICache",
                                            "port": "io.cpu.req.valid"}}}]},
                # 第二轮(拒绝后重做): 干净的 CONJUNCT
                conj_decision(), conj_decision(),
            ]

            with mock.patch.object(dp, "decompose",
                                   side_effect=bad_then_good), \
                 mock.patch.object(dp, "critique",
                                   side_effect=lambda c: {
                                       "evidence": "e", "hint": "h"}), \
                 mock.patch.object(dp, "cha_verify"):
                d = self._mk(v)
                rep = d.run()

            # 1) 虚假假设被全局筛拦截并记账
            causes = [f.cause for f in d.st.failures]
            self.assertIn("ASSUME_FALSIFIED", causes)
            # 2) 树上不留该假设(回滚清理, 无债务螺旋起点)
            live = [n.formula for n in d.st.nodes.values()
                    if n.kind == "assume"]
            self.assertNotIn("F cpuReq", live)
            # 3) 全局筛确实对 assume 跑过(与 children 同等)
            self.assertTrue(any("cpuReq" in f for f in screen_calls))
        finally:
            dp.SEARCH_MODE = "dfs"

    def _mk(self, v):
        d = Path(tempfile.mkdtemp())
        (d / "h.json").write_text(json.dumps(
            TestQuickVerifyFailRequeue.HIER_REAL), encoding="utf-8")
        (d / "p.json").write_text(json.dumps({
            "id": "P1", "formula": "F resp",
            "signals": {"resp": {"module": "ICache",
                                 "port": "io.cpu.resp.valid"}}}
        ), encoding="utf-8")
        return dp.Dispatcher(str(d / "h.json"), str(d / "p.json"),
                             reader=FakeReader(), verifier=v)


class TestTimeoutChildFeedback(unittest.TestCase):
    """超时上限子结点: 反馈 decomposer 换方案 + 此次分解不算(尝试计数退还)。"""

    def test_feedback_and_refund(self):
        dp.SEARCH_MODE = "bfs"
        try:
            import test_proof_state as tp
            # 预置: 某等价签名已超时 5 次
            def v(module, signals, assert_formula, assumes, mode, **k):
                return {"verdict": "PASS", "detail": ""}

            dec_calls = []

            def dec(ctx):
                dec_calls.append(ctx["待验证性质(当前分解目标, node)"]
                                 ["formula"])
                if len(dec_calls) == 1:
                    return {"strategy": "CONJUNCT", "rationale": "r",
                            "children": [
                                {"id": "C1", "nl": "难兑现",
                                 "formula": "F(rdy)",
                                 "signals": {"rdy": {"module": "ICache",
                                                     "port": "io.nasti.ar.ready"}}}]}
                return conj2_decision()

            d0 = Path(tempfile.mkdtemp())
            (d0 / "h.json").write_text(json.dumps(
                TestQuickVerifyFailRequeue.HIER_REAL), encoding="utf-8")
            (d0 / "p.json").write_text(json.dumps({
                "id": "P1", "formula": "F resp",
                "signals": {"resp": {"module": "ICache",
                                     "port": "io.cpu.resp.valid"}}}
            ), encoding="utf-8")
            disp = dp.Dispatcher(str(d0 / "h.json"), str(d0 / "p.json"),
                                 reader=FakeReader(), verifier=v)
            # 烧满超时上限(同签名)——直接预置计数, 不污染 root 子树
            wid = ps.wire_id_of({"module": "ICache",
                                 "port": "io.nasti.ar.ready"}, disp.st.h)
            disp.st.timeout_attempts[ps.signature("F(rdy)", [wid])] = \
                ps.TIMEOUT_RETRY_MAX

            with mock.patch.object(dp, "decompose", side_effect=dec), \
                 mock.patch.object(dp, "critique",
                                   side_effect=lambda c: {"evidence": "e",
                                                          "hint": "h"}), \
                 mock.patch.object(dp, "cha_verify"):
                rep = disp.run()

            # 1) 反馈入账(挂在父节点上, decomposer 下轮可见)
            fb = [f for f in disp.st.failures
                  if f.cause == "TIMEOUT_RETRY_EXCEEDED"
                  and f.node == disp.st.root]
            self.assertTrue(fb)
            # 2) decomposer 被再次调用(未被尝试上限 SKIP, 计数已退还)
            self.assertGreater(len(dec_calls), 1)
            # 3) 全局筛没有为超时子结点跑(开场短路)
        finally:
            dp.SEARCH_MODE = "dfs"


class TestLazyKbReuse(unittest.TestCase):
    """延迟复用: B 进树时 A 未证毕, B 激活前 A 已入 KB → 弹栈时重查命中,
    免分解直接 PROVEN (2026-09-28 用户场景)。"""

    def test_reuse_on_activation(self):
        dp.SEARCH_MODE = "bfs"
        try:
            def v(module, signals, assert_formula, assumes, mode, **k):
                return {"verdict": "PASS", "detail": ""}

            d = Path(tempfile.mkdtemp())
            (d / "h.json").write_text(json.dumps(
                TestQuickVerifyFailRequeue.HIER_REAL), encoding="utf-8")
            (d / "p.json").write_text(json.dumps({
                "id": "P1", "formula": "F resp",
                "signals": {"resp": {"module": "ICache",
                                     "port": "io.cpu.resp.valid"}}}
            ), encoding="utf-8")
            disp = dp.Dispatcher(str(d / "h.json"), str(d / "p.json"),
                                 reader=FakeReader(), verifier=v)
            disp.run_dir.mkdir(parents=True, exist_ok=True)
            st = disp.st
            # B 进树(此刻 KB 空, 创建查重落空), 保持 PENDING 压栈
            st.nodes[st.root].strategy = "CONJUNCT"
            b_id = st.add_property(st.root, {
                "id": "B", "nl": "b", "formula": "F(rdy)",
                "signals": {"rdy": {"module": "ICache",
                                    "port": "io.nasti.ar.ready"}}})["id"]
            self.assertEqual(st.nodes[b_id].status, ps.PENDING)
            # A 在别处证毕入 KB(同签名)
            wid = ps.wire_id_of({"module": "ICache",
                                 "port": "io.nasti.ar.ready"}, st.h)
            st.kb.add("F(rdy)", [wid], "N99", "A 定理",
                      signals={"rdy": {"module": "ICache",
                                       "port": "io.nasti.ar.ready"}},
                      level=2)
            # B 激活: 延迟复用, 不调 decomposer 直接 PROVEN
            dec_calls = []
            with mock.patch.object(dp, "decompose",
                                   side_effect=lambda c: dec_calls.append(1)):
                st.stack.append(b_id)
                disp._step()
            self.assertEqual(st.nodes[b_id].status, ps.IC3_PROVEN)
            self.assertEqual(st.nodes[b_id].reuse_from, "T1")
            self.assertEqual(len(dec_calls), 0)   # 未烧 LLM
        finally:
            dp.SEARCH_MODE = "dfs"


class TestVacuousAssumeAndPrune(unittest.TestCase):
    """N86/N135 教训的两项修复: 恒真式假设拒绝 + 失败轮 assume 清扫。"""

    def test_prune_stale_assumes(self):
        st = tp.mk_state()
        st.nodes[st.root].strategy = "ASSUME"
        a1 = st.add_assume(st.root, {
            "id": "A1", "nl": "旧假设(将失败)", "formula": "G(rdy)",
            "signals": {"rdy": {"module": "ICache",
                                "port": "io.nasti.ar.ready"}}})
        did1 = st.nodes[a1].discharged_by
        # 新一轮只保留另一条 → 旧假设被清扫
        a2 = st.add_assume(st.root, {
            "id": "A2", "nl": "新假设", "formula": "F(rdy)",
            "signals": {"rdy": {"module": "ICache",
                                "port": "io.nasti.ar.ready"}}})
        n = st.prune_stale_assumes(st.root, ["F(rdy)"])
        self.assertEqual(n, 2)               # assume + 其兑现节点
        self.assertNotIn(did1, st.nodes)
        self.assertNotIn(a1, st.nodes)
        self.assertIn(a2, st.nodes)
        self.assertEqual(st.nodes[st.root].assumes, [a2])
        self.assertNotIn(did1, st.stack)


class TestVerifyMemo(unittest.TestCase):
    """验证记忆化: 同(公式,前提,模块,引擎,信号)重验命中缓存, 不重跑 sbt。"""

    def test_memo_hit_and_premise_sensitivity(self):
        calls = []

        def v(module, signals, assert_formula, assumes, mode, **k):
            calls.append((module, mode, assert_formula, tuple(assumes)))
            return {"verdict": "FAIL", "detail": "cex@3"}

        d = mk_dispatcher(v)
        f = "a -> F b"
        s = {"a": {"module": "ICache", "port": "io.a"},
             "b": {"module": "ICache", "port": "io.b"}}
        r1 = d.verifier(module="ICache", signals=s, assert_formula=f,
                        assumes=[], mode="bmc")
        r2 = d.verifier(module="ICache", signals=s, assert_formula=f,
                        assumes=[], mode="bmc")
        # 1) 命中: 真实调用只有 1 次, 第二次回放缓存
        self.assertEqual(len(calls), 1)
        self.assertEqual(r2["verdict"], "FAIL")
        self.assertIn("缓存命中", r2["detail"])
        self.assertEqual(d._memo_hits, 1)
        # 2) 前提变化 → 键变化 → 重跑
        r3 = d.verifier(module="ICache", signals=s, assert_formula=f,
                        assumes=["G !c"], mode="bmc")
        self.assertEqual(len(calls), 2)
        self.assertNotIn("缓存命中", r3["detail"])
        # 3) 公式变化 → 重跑
        r4 = d.verifier(module="ICache", signals=s, assert_formula="a -> F c",
                        assumes=[], mode="bmc")
        self.assertEqual(len(calls), 3)
        # 4) 空白差异不构成新键
        r5 = d.verifier(module="ICache", signals=s,
                        assert_formula="a ->  F b", assumes=[], mode="bmc")
        self.assertEqual(len(calls), 3)
        self.assertEqual(d._memo_hits, 2)


class TestGuards(unittest.TestCase):
    """结论输入守卫(保守) + LTL 语法预检。"""

    def test_conclusion_input_guard(self):
        # ICache.io.* 在 FakeReader 中是 Input → 结论为单一该类信号应拦截
        d = mk_dispatcher(lambda **k: {"verdict": "PASS", "detail": ""})
        st = d.st
        st.nodes[st.root].strategy = "CONJUNCT"
        # 结论 F b, b 为 Input
        f = "a -> F b"
        r = st.add_property(st.root, {
            "id": "C1", "nl": "x", "formula": f,
            "signals": {"a": {"module": "ICache", "port": "io.a"},
                        "b": {"module": "ICache", "port": "io.b"}}})
        self.assertTrue(d._conclusion_input_guard(st.root, r["id"]))
        # failure 由调用方(BFS children 循环)记录, guard 本身只做检测
        # 结论为 Output 信号不触发(Datapath.imem* 在 FakeReader 是 Output)
        r2 = st.add_property(st.root, {
            "id": "C2", "nl": "x", "formula": "b -> F imemReq",
            "signals": {"imemReq": {"module": "Datapath", "port": "imem.req"},
                        "b": {"module": "ICache", "port": "io.b"}}})
        self.assertFalse(d._conclusion_input_guard(st.root, r2["id"]))
        # 复合结论全 Input → 触发(2026-10-09 放宽后); 混合方向不触发
        r3 = st.add_property(st.root, {
            "id": "C3", "nl": "x", "formula": "a -> F (b & imemReq)",
            "signals": {"a": {"module": "ICache", "port": "io.a"},
                        "b": {"module": "ICache", "port": "io.b"},
                        "imemReq": {"module": "Datapath",
                                    "port": "imem.req"}}})
        self.assertFalse(d._conclusion_input_guard(st.root, r3["id"]))

    def test_ltl_syntax_check(self):
        d = mk_dispatcher(lambda **k: {"verdict": "PASS", "detail": ""})
        c = d._ltl_syntax_check
        self.assertIsNone(c("a -> F b"))
        self.assertIsNone(c("(a & !b) ##1 (a & b)"))
        self.assertIsNotNone(c("(a && !b) ##1 c"))      # 序列层 &&
        self.assertIsNotNone(c("a ##1 F b"))             # ## 接性质层
        self.assertIsNotNone(c("a -> (b ##1 c)"))        # -> 入序列操作数


class TestKBDefaultPremises(unittest.TestCase):
    """KB 默认前提: 相关且可见的已证定理烘进模块验证的 assumes。"""

    def test_bake_relevant_visible_only(self):
        seen = {}

        def v(module, signals, assert_formula, assumes, mode, **k):
            seen['assumes'] = list(assumes)
            seen['module'] = module
            return {"verdict": "PASS", "detail": ""}

        d = mk_dispatcher(v)
        st = d.st
        # 树上节点: 结论引用 io.a
        st.nodes[st.root].strategy = "CONJUNCT"
        r = st.add_property(st.root, {
            "id": "C1", "nl": "x", "formula": "b -> F a",
            "signals": {"a": {"module": "Datapath", "port": "imem.req"},
                        "b": {"module": "ICache", "port": "io.b"}}})
        # KB 一条相关定理(同 imem.req 网络, Datapath 视角)
        st.kb.add("imemReq -> F imemAck", [ps.wire_id_of(
            {"module": "Datapath", "port": "imem.req"}, st.h)], "N99", "t",
            signals={"imemReq": {"module": "Datapath", "port": "imem.req"},
                     "imemAck": {"module": "Datapath", "port": "imem.ack"}},
            level=2)
        # 注册 imem.ack 视图(可见性依赖 registry views)
        st.registry.register("N98", {"imemAck": {
            "module": "Datapath", "port": "imem.ack"}})
        raw = d.run_module_ic3(r["id"])
        # 相关定理被烘入
        self.assertTrue(any(a.replace(" ", "") == "imemReq->FimemAck"
                            for a in seen['assumes']))
        # 溯源标记
        self.assertIn("KB前提", str(raw.get("detail", "")) +
                      str(seen.get('assumes')))


class TestChainAssumesAndKbFamily(unittest.TestCase):
    """3a 链上有效假设块 + 3c KB 形状族摘要。"""

    def test_blocks(self):
        d = mk_dispatcher(lambda **k: {"verdict": "PASS", "detail": ""})
        st = d.st
        st.nodes[st.root].strategy = "ASSUME"
        st.add_assume(st.root, {
            "id": "A1", "nl": "t", "formula": "G(rdy)",
            "signals": {"rdy": {"module": "ICache",
                                "port": "io.nasti.ar.ready"}}})
        st.stack.append(st.root)
        blk = d._chain_assumes(st.root)
        self.assertEqual(len(blk), 1)
        self.assertIn("G(rdy)", blk[0]["formula"])
        fam = d._kb_family_summary()
        self.assertIsInstance(fam, dict)


class TestBmcFirstMode(unittest.TestCase):
    """bmc_first 模式: 中间节点只跑 BMC, KB 容忍 bmc 级, 批量 IC3 延后。"""

    def setUp(self):
        self._orig = dp.VERIFY_MODE
        dp.VERIFY_MODE = "bmc_first"
        ps.CONFIG["verify_mode"] = "bmc_first"

    def tearDown(self):
        dp.VERIFY_MODE = self._orig
        ps.CONFIG["verify_mode"] = self._orig

    def test_bmc_only_no_ic3(self):
        """bmc_first: module 验证只调 bmc, 不调 ic3。"""
        modes = []

        def v(module, signals, assert_formula, assumes, mode, **k):
            modes.append(mode)
            return {"verdict": "PASS", "detail": ""}

        d = mk_dispatcher(v)
        st = d.st
        st.nodes[st.root].strategy = "CONJUNCT"
        r = st.add_property(st.root, {
            "id": "C1", "nl": "x", "formula": "a -> F b",
            "signals": {"a": {"module": "Datapath", "port": "imem.req"},
                        "b": {"module": "Datapath", "port": "imem.ack"}}})
        raw = d.run_module_ic3(r["id"])
        self.assertEqual(raw["verdict"], "PASS")
        self.assertIn("IC3 deferred", raw.get("detail", ""))
        self.assertIn("bmc", modes)
        self.assertNotIn("ic3", modes)  # 不应调用 ic3

    def test_kb_accepts_bmc_level(self):
        """bmc_first: BMC_FILTERED 节点也入 KB, proof_strength=bmc。"""
        st = tp.mk_state()
        ps.CONFIG["verify_mode"] = "bmc_first"
        st.nodes[st.root].strategy = "CONJUNCT"
        r = st.add_property(st.root, {
            "id": "C1", "nl": "x", "formula": "G(a)",
            "signals": {"a": {"module": "ICache", "port": "io.a"}}})
        st.mark(r["id"], ps.BMC_FILTERED)
        self.assertTrue(st.try_kb_ingest(r["id"]))
        self.assertEqual(len(st.kb.entries), 1)
        self.assertEqual(st.kb.entries[0].proof_strength, "bmc")
        ps.CONFIG["verify_mode"] = "standard"
        # standard 模式下 BMC_FILTERED 不入库
        r2 = st.add_property(st.root, {
            "id": "C2", "nl": "x", "formula": "F(a)",
            "signals": {"a": {"module": "ICache", "port": "io.a"}}})
        st.mark(r2["id"], ps.BMC_FILTERED)
        self.assertFalse(st.try_kb_ingest(r2["id"]))

    def test_kb_remove(self):
        """KB.remove 按 kid 移除。"""
        st = tp.mk_state()
        st.nodes[st.root].strategy = "CONJUNCT"
        r = st.add_property(st.root, {
            "id": "C1", "nl": "x", "formula": "G(a)",
            "signals": {"a": {"module": "ICache", "port": "io.a"}}})
        st.mark(r["id"], ps.IC3_PROVEN)
        kid = st.kb.entries[0].kid
        self.assertTrue(st.kb.remove(kid))
        self.assertEqual(len(st.kb.entries), 0)
        self.assertFalse(st.kb.remove(kid))


class TestGuardMultiAtom(unittest.TestCase):
    """结论守卫放宽: 多原子结论全 Input 才触发, 混合方向不触发。"""

    def test_multi_atom(self):
        d = mk_dispatcher(lambda **k: {"verdict": "PASS", "detail": ""})
        st = d.st
        st.nodes[st.root].strategy = "CONJUNCT"
        # 全 Input: a -> F (b & c) → 应触发
        r1 = st.add_property(st.root, {
            "id": "M1", "nl": "x", "formula": "a -> F (b & c)",
            "signals": {"a": {"module": "ICache", "port": "io.a"},
                        "b": {"module": "ICache", "port": "io.b"},
                        "c": {"module": "ICache", "port": "io.c"}}})
        self.assertTrue(d._conclusion_input_guard(st.root, r1["id"]))
        # 混合: a -> F (b & imemReq) → b 是 Input 但 imemReq 是 Output → 不触发
        r2 = st.add_property(st.root, {
            "id": "M2", "nl": "x", "formula": "a -> F (b & imemReq)",
            "signals": {"a": {"module": "ICache", "port": "io.a"},
                        "b": {"module": "ICache", "port": "io.b"},
                        "imemReq": {"module": "Datapath",
                                    "port": "imem.req"}}})
        self.assertFalse(d._conclusion_input_guard(st.root, r2["id"]))
