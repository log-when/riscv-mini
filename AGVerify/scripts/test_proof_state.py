#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""proof_state 单元测试: 合成 hierarchy, 手工 mark 模拟 CHA 结果, 不跑 sbt"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from classify_prop import DesignReader, Hierarchy
import proof_state as ps

HIER = {
    "modules": [
        {"name": "Tile"},
        {"name": "Datapath", "inst": "core", "parent": "Tile"},
        {"name": "ICache", "inst": "icache", "parent": "Tile"},
        {"name": "DCache", "inst": "dcache", "parent": "Tile"},
    ],
    "connections": [
        {"from": "Datapath.imem", "to": "ICache.io"},
        {"from": "Datapath.dmem", "to": "DCache.io"},
    ],
}


class FakeReader(DesignReader):
    """端口方向: Datapath 的 imem/dmem 为 Output, cache 的 io 为 Input"""
    def port_direction(self, module, port):
        top = port.split(".", 1)[0]
        if module == "Datapath" and top in ("imem", "dmem"):
            return "Output"
        if module in ("ICache", "DCache") and top == "io":
            return "Input"
        return None


def mk_state():
    p = Path(tempfile.mkdtemp()) / "h.json"
    p.write_text(json.dumps(HIER), encoding="utf-8")
    h = Hierarchy.load(str(p))
    return ps.ProofState(h, FakeReader(),
                         {"id": "P1", "formula": "G(req -> F resp)",
                          "signals": {"req": {"module": "ICache",
                                              "port": "io.cpu.req.valid"},
                                      "resp": {"module": "ICache",
                                               "port": "io.cpu.resp.valid"}}})


def assume_spec(formula="G(ar_ready)", signals=None):
    return {"formula": formula, "nl": "env",
            "signals": signals or {
                "ar_ready": {"module": "ICache",
                             "port": "io.nasti.ar.ready"}}}


class TestLifecycle(unittest.TestCase):
    def test_conjunct_flow(self):
        st = mk_state()
        r1 = st.add_property(st.root, {"formula": "G(a)",
                                       "signals": {"a": {"module": "ICache",
                                                         "port": "io.cpu.abort"}}})
        st.mark(r1["id"], ps.BMC_FILTERED)
        st.mark(r1["id"], ps.IC3_PROVEN)
        # 复用: 同公式同 wire 的新节点直接 PROVEN
        r2 = st.add_property(st.root, {"formula": "G(a)",
                                       "signals": {"a": {"module": "ICache",
                                                         "port": "io.cpu.abort"}}})
        self.assertEqual(r2["reused_from"], "T1")
        self.assertEqual(st.nodes[r2["id"]].status, ps.IC3_PROVEN)
        st.mark(st.root, ps.BMC_FILTERED)
        st.mark(st.root, ps.IC3_PROVEN)
        self.assertTrue(st.done())

    def test_assume_flow_with_mod_proven(self):
        st = mk_state()
        # 分解为 ASSUME 路
        st.nodes[st.root].strategy = "ASSUME"
        aid = st.add_assume(st.root, assume_spec())
        # 模块 IC3 过 → MOD_PROVEN（不进 KB）
        st.mark(st.root, ps.BMC_FILTERED)
        st.mark(st.root, ps.MOD_PROVEN)
        self.assertEqual(len(st.kb.entries), 0)
        # 兑现子任务（栈顶）完成
        did = st.nodes[aid].discharged_by
        st.mark(did, ps.BMC_FILTERED)
        st.mark(did, ps.IC3_PROVEN)
        st.mark(st.root, ps.IC3_PROVEN)      # 升级
        self.assertEqual(len(st.kb.entries), 2)  # 兑现定理 + root 定理
        self.assertTrue(st.done())

    def test_assume_violated_rollback(self):
        st = mk_state()
        st.nodes[st.root].strategy = "ASSUME"
        aid = st.add_assume(st.root, assume_spec())
        st.mark(st.root, ps.BMC_FILTERED)
        st.mark(st.root, ps.MOD_PROVEN)
        did = st.nodes[aid].discharged_by
        st.mark(did, ps.BMC_FAILED)
        level = st.record_failure(did, "VIOLATED",
                                  cause="CONTRADICT_ASSUME")
        self.assertEqual(level, "local")
        # 反 KB 已记录
        self.assertIsNotNone(st.neg_kb.lookup(
            "G(ar_ready)", [ps.wire_id_of(
                {"module": "ICache", "port": "io.nasti.ar.ready"}, st.h)],
            signals={"ar_ready": {"module": "ICache",
                                  "port": "io.nasti.ar.ready"}},
            level=3))
        # 回滚: root 从 MOD_PROVEN 回 PENDING, 兑现节点删除
        st.rollback(st.root)
        self.assertEqual(st.nodes[st.root].status, ps.PENDING)
        self.assertNotIn(did, st.nodes)
        self.assertEqual(len(st.failures), 1)   # 失败历史保留

    def test_neg_kb_short_circuit(self):
        st = mk_state()
        st.nodes[st.root].strategy = "ASSUME"
        aid = st.add_assume(st.root, assume_spec())
        did = st.nodes[aid].discharged_by
        st.mark(did, ps.BMC_FAILED)
        st.record_failure(did, "VIOLATED")
        st.rollback(st.root)
        # 重试时 decomposer 又提出同签名 assume → 其兑现节点开场即短路
        st.nodes[st.root].strategy = "ASSUME"
        aid2 = st.add_assume(st.root, assume_spec())
        did2 = st.nodes[aid2].discharged_by
        self.assertEqual(st.nodes[did2].status, ps.BMC_FAILED)


class TestCycleGuard(unittest.TestCase):
    def test_pending_obligation_cycle_rejected(self):
        st = mk_state()
        st.nodes[st.root].strategy = "ASSUME"
        aid = st.add_assume(st.root, assume_spec())
        did = st.nodes[aid].discharged_by          # 兑现任务在栈上
        # 在兑现任务里又提出同签名 assume（针对 Datapath 侧写法不同也行,
        # 这里用同一 ICache 视角最直接）
        with self.assertRaises(ps.ProofStateError) as cm:
            st.add_assume(did, assume_spec())
        self.assertIn("嵌套", str(cm.exception))  # 嵌套检查先于循环

    def test_depth_budget(self):
        st = mk_state()
        cur = st.root
        for i in range(ps.MAX_DEPTH + 1):
            try:
                r = st.add_property(cur, {
                    "formula": f"G(d{i})",
                    "signals": {"d": {"module": "ICache",
                                      "port": f"io.d{i}"}}})
            except ps.ProofStateError as e:
                self.assertIn("深度超限", str(e))
                return
            cur = r["id"]
        self.fail("未触发深度限制")

    def test_assume_nesting_rejected(self):
        st = mk_state()
        st.nodes[st.root].strategy = "ASSUME"
        aid = st.add_assume(st.root, assume_spec())
        with self.assertRaises(ps.ProofStateError) as cm:
            st.add_assume(aid, assume_spec(formula="G(nest)"))
        self.assertIn("嵌套", str(cm.exception))
        did = st.nodes[aid].discharged_by
        with self.assertRaises(ps.ProofStateError) as cm:
            st.add_assume(did, assume_spec(formula="G(nest2)"))
        self.assertIn("嵌套", str(cm.exception))

    def test_attempt_counters(self):
        st = mk_state()
        r1 = st.add_property(st.root, {
            "formula": "G(x)", "signals": {"x": {"module": "ICache",
                                                 "port": "io.cpu.abort"}}})
        # r1 在 depth=1, 允许 ceil(20/2)=10 次
        allowed = ps._rollback_allowed(st.nodes[r1["id"]].depth)
        for i in range(allowed):
            self.assertTrue(st.register_attempt(r1["id"]))
        self.assertFalse(st.register_attempt(r1["id"]))   # 超限 → SKIP
        st.reset_attempt(r1["id"])
        self.assertTrue(st.register_attempt(r1["id"]))    # 重遇重置
        # 深层允许次数递减
        deep = st.add_property(st.root, {
            "formula": "G(dd)", "signals": {"dd": {"module": "ICache",
                                                   "port": "io.dd"}}})
        for i in range(ps._rollback_allowed(1)):
            self.assertTrue(st.register_attempt(deep["id"]))
        self.assertFalse(st.register_attempt(deep["id"]))

    def test_structural_cycle_check_passes(self):
        st = mk_state()
        st.add_property(st.root, {"formula": "G(b)",
                                  "signals": {"b": {"module": "DCache",
                                                    "port": "io.cpu.abort"}}})
        st.check_cycles()      # 不抛错


class TestRegistry(unittest.TestCase):
    def test_wire_unification(self):
        st = mk_state()
        # 同一 imem 连线两种视角 → 同一 wire_id
        w1 = ps.wire_id_of({"module": "Datapath", "port": "imem.req.valid"}, st.h)
        w2 = ps.wire_id_of({"module": "ICache", "port": "io.req.valid"}, st.h)
        self.assertEqual(w1, w2)
        # 不同字段 → 不同线
        w3 = ps.wire_id_of({"module": "ICache", "port": "io.resp.valid"}, st.h)
        self.assertNotEqual(w2, w3)
        # 未连接信号 → sig:
        w4 = ps.wire_id_of({"module": "ICache", "port": "internal.state"}, st.h)
        self.assertTrue(w4.startswith("sig:"))

    def test_writer_directions(self):
        st = mk_state()
        wid = ps.wire_id_of({"module": "ICache", "port": "io.req.valid"}, st.h)
        r = st.add_property(st.root, {
            "formula": "G(x)",
            "signals": {"x": {"module": "Datapath",
                              "port": "imem.req.valid"}}})
        e = st.registry.entries[wid]
        self.assertEqual(e.writer, "Datapath")
        self.assertEqual(e.readers, {"ICache"})
        self.assertEqual(st.registry.wire_ids_of(r["id"]), [wid])


class TestInputSideGuard(unittest.TestCase):
    def test_output_side_assume_rejected(self):
        st = mk_state()
        st.nodes[st.root].strategy = "ASSUME"
        bad = {"formula": "G(x)", "signals": {
            "x": {"module": "Datapath", "port": "imem.req.valid"}}}
        with self.assertRaises(ps.ProofStateError) as cm:
            st.add_assume(st.root, bad)
        self.assertIn("书写错误", str(cm.exception))


class TestSnapshot(unittest.TestCase):
    def test_roundtrip(self):
        st = mk_state()
        r = st.add_property(st.root, {"formula": "G(a)",
                                      "signals": {"a": {"module": "ICache",
                                                        "port": "io.cpu.abort"}}})
        st.mark(r["id"], ps.BMC_FILTERED)
        st.mark(r["id"], ps.IC3_PROVEN)
        p = Path(tempfile.mkdtemp()) / "snap.json"
        st.snapshot(str(p))
        obj = json.loads(p.read_text())
        self.assertEqual(obj["root"], st.root)
        self.assertIn("kb", obj)
        self.assertIn("neg_kb", obj)
        self.assertEqual(len(obj["nodes"]), 2)


if __name__ == "__main__":
    unittest.main()


class TestTimeoutRetryBound(unittest.TestCase):
    """等价性质超时重试上限: TIMEOUT 不证伪可再试, 但同签名达
    timeout_retry_max 次后, 新节点(含兑现节点)开场短路不再验证。"""

    def test_bound_short_circuits_new_nodes(self):
        st = mk_state()
        # 两次 TIMEOUT 同签名 → 计数达上限
        for i in range(ps.TIMEOUT_RETRY_MAX):
            st.nodes[st.root].strategy = "CONJUNCT"
            r = st.add_property(st.root, {
                "id": f"C{i}", "nl": "t", "formula": "F(rdy)",
                "signals": {"rdy": {"module": "ICache",
                                    "port": "io.nasti.ar.ready"}}})
            st.mark(r["id"], ps.TIMEOUT_UNPROVED)
        # 第三次提议同签名: 开场短路
        r3 = st.add_property(st.root, {
            "id": "C9", "nl": "t", "formula": "F(rdy)",
            "signals": {"rdy": {"module": "ICache",
                                "port": "io.nasti.ar.ready"}}})
        self.assertTrue(r3["short_circuited"])
        self.assertEqual(st.nodes[r3["id"]].status, ps.TIMEOUT_UNPROVED)
        # 兑现节点同样短路(不压栈)
        st.nodes[st.root].strategy = "ASSUME"
        aid = st.add_assume(st.root, {
            "id": "A9", "nl": "t", "formula": "F(rdy)",
            "signals": {"rdy": {"module": "ICache",
                                "port": "io.nasti.ar.ready"}}})
        did = st.nodes[aid].discharged_by
        self.assertEqual(st.nodes[did].status, ps.TIMEOUT_UNPROVED)
        self.assertNotIn(did, st.stack)
        # 记账含原因
        self.assertTrue(any(f.cause == "TIMEOUT_RETRY_EXCEEDED"
                            for f in st.failures))


class TestQuickVerifyFailNotNegKb(unittest.TestCase):
    """QUICK_VERIFY_FAIL(多落点快检全败, 全局BMC已通过)不是证伪:
    记账入 failures 但不进反 KB, 不得阻断同式性质的后续尝试。"""

    def test_not_polluting_neg_kb(self):
        st = mk_state()
        st.nodes[st.root].strategy = "CONJUNCT"
        r = st.add_property(st.root, {
            "id": "C1", "nl": "t", "formula": "F(rdy)",
            "signals": {"rdy": {"module": "ICache",
                                "port": "io.nasti.ar.ready"}}})
        st.record_failure(r["id"], "MODULE_STUCK",
                          cause="QUICK_VERIFY_FAIL",
                          evidence="全局过, 模块级卡住")
        # 记账在案
        self.assertTrue(any(f.cause == "QUICK_VERIFY_FAIL"
                            for f in st.failures))
        # 反 KB 干净: 同式新节点不被短路
        self.assertIsNone(st.neg_kb.lookup(
            "F(rdy)", [ps.wire_id_of(
                {"module": "ICache", "port": "io.nasti.ar.ready"}, st.h)],
            signals={"rdy": {"module": "ICache",
                             "port": "io.nasti.ar.ready"}}, level=3))
        # 对照: 真证伪(ASSUME_FALSIFIED)仍进反 KB
        st.record_failure(r["id"], "VIOLATED", cause="ASSUME_FALSIFIED")
        self.assertIsNotNone(st.neg_kb.lookup(
            "F(rdy)", [ps.wire_id_of(
                {"module": "ICache", "port": "io.nasti.ar.ready"}, st.h)],
            signals={"rdy": {"module": "ICache",
                             "port": "io.nasti.ar.ready"}}, level=3))


class TestKBIngestionGate(unittest.TestCase):
    """入库门禁: 未清偿 assume 的条件证毕不入 KB; 债清后补录。"""

    def test_gate_and_late_ingestion(self):
        st = mk_state()
        st.nodes[st.root].strategy = "ASSUME"
        aid = st.add_assume(st.root, assume_spec())
        did = st.nodes[aid].discharged_by
        # 债未清: 根标 IC3_PROVEN 不入 KB
        st.mark(st.root, ps.IC3_PROVEN)
        self.assertEqual(len(st.kb.entries), 0)
        # 债清: 兑现节点证毕 → 向上补录根
        st.mark(did, ps.IC3_PROVEN)
        # 两条: 兑现节点自身(无条件定理) + 根(债清补录)
        origins = {e.node_origin for e in st.kb.entries}
        self.assertEqual(origins, {did, st.root})
        # 幂等: 再标不重复入库
        st.try_kb_ingest(st.root)
        st.try_kb_ingest(did)
        self.assertEqual(len(st.kb.entries), 2)


class TestFuzzyPort(unittest.TestCase):
    """4a: 端口名近似匹配(唯一候选才纠正)。"""

    def test_fuzzy(self):
        self.assertEqual(ps.ProofState._fuzzy_port(
            "io.cpu.req.vaid", {"io.cpu.req.valid": "Input",
                                "io.cpu.resp.valid": "Output"}),
            "io.cpu.req.valid")
        # 多候选不猜
        self.assertIsNone(ps.ProofState._fuzzy_port(
            "io.cpu.re", {"io.cpu.req.valid": "I", "io.cpu.resp.valid": "O"}))
        self.assertIsNone(ps.ProofState._fuzzy_port("zzz", {}))
