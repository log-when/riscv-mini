#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""classify_prop 单元测试（纯逻辑, 用合成 hierarchy, 不依赖真实 Chisel）"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from classify_prop import (ClassifyError, Hierarchy, classify, DesignReader)


HIER = {
    "modules": [
        {"name": "Tile", "src": "src/main/scala/mini/Tile.scala"},
        {"name": "Datapath", "inst": "core", "parent": "Tile", "src": ""},
        {"name": "ICache", "inst": "icache", "parent": "Tile", "src": ""},
        {"name": "DCache", "inst": "dcache", "parent": "Tile", "src": ""},
    ],
    "connections": [
        {"from": "Datapath.io.icache", "to": "ICache.io.cpu"},
        {"from": "Datapath.io.dcache", "to": "DCache.io.cpu"},
    ],
}


class FakeReader(DesignReader):
    def port_direction(self, module, port):
        return None


def mk_hier(tmpdir: Path) -> Path:
    p = tmpdir / "hierarchy.json"
    p.write_text(json.dumps(HIER), encoding="utf-8")
    return p


def prop(signals, scope=None, module=None):
    d = {"id": "P1", "formula": "G(a -> F b)", "signals": signals}
    if scope:
        d["scope"] = scope
    if module:
        d["module"] = module
    return d


S_DCACHE_ONLY = {
    "hit": {"module": "DCache", "port": "io.cpu.resp.valid"},
    "req": {"module": "DCache", "port": "io.cpu.req.valid"},
}
S_CROSS_TILE = {
    "req": {"module": "ICache", "port": "io.cpu.req.valid"},
    "hit": {"module": "DCache", "port": "io.cpu.resp.valid"},
}
S_SAME_WIRE = {
    # Datapath.io.icache <-> ICache.io.cpu 连接: 同一根连线两种视角 -> atomic
    "req":  {"module": "Datapath", "port": "io.icache.req.valid"},
    "req2": {"module": "ICache",   "port": "io.cpu.req.valid"},
}
S_DIFF_WIRE_SAME_PARENT = {
    # 同在 Tile 内但不同连线 -> composite（无法在单一子模块中验证）
    "req":  {"module": "Datapath", "port": "imem.req.valid"},
    "resp": {"module": "ICache",   "port": "io.resp.valid"},
}


class TestClassify(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        self.h = Hierarchy.load(str(mk_hier(Path(self.tmp))))
        self.reader = FakeReader()

    def test_single_module_atomic(self):
        r = classify(prop(S_DCACHE_ONLY, "atomic"), self.h, self.reader)
        self.assertEqual(r["derived"]["scope"], "atomic")
        self.assertEqual(r["derived"]["module"], "DCache")

    def test_cross_modules_atomic_at_datapath(self):
        # ICache/DCache 的信号分别是 imem/dmem 连线, 都是 Datapath 的
        # 端口 -> 落在同一子模块 Datapath -> atomic, 信号合一到其视角
        r = classify(prop(S_CROSS_TILE, "atomic", "Datapath"), self.h, self.reader)
        self.assertEqual(r["derived"]["scope"], "atomic")
        self.assertEqual(r["derived"]["module"], "Datapath")
        sig = r["derived"]["signals"]
        self.assertEqual(sig["req"]["port"], "io.icache.req.valid")
        self.assertEqual(sig["req"]["via"], "ICache.io.cpu.req.valid")
        self.assertEqual(sig["hit"]["port"], "io.dcache.resp.valid")

    def test_same_wire_two_views_atomic(self):
        # 同一根连线的两种视角 -> atomic, 归属首个信号宿主 Datapath
        r = classify(prop(S_SAME_WIRE, "atomic", "Datapath"), self.h, self.reader)
        self.assertEqual(r["derived"]["scope"], "atomic")
        self.assertEqual(r["derived"]["module"], "Datapath")
        sig = r["derived"]["signals"]
        # req2 从 ICache 视角合一为 Datapath 视角
        self.assertEqual(sig["req2"]["port"], "io.icache.req.valid")
        self.assertEqual(sig["req2"]["via"], "ICache.io.cpu.req.valid")

    def test_unconnected_port_composite(self):
        # ICache 的 debug 端口未连接, 无法与 DCache 信号落入同一子模块
        s = {"x": {"module": "ICache", "port": "debug.out"},
             "y": {"module": "DCache", "port": "io.cpu.req.valid"}}
        r = classify(prop(s, "composite"), self.h, self.reader)
        self.assertEqual(r["derived"]["scope"], "composite")

    def test_declaration_gate_reject(self):
        # 声明 atomic 归属 Datapath, 但 debug 端口无法以 Datapath 视角
        # 表达 -> 一致性门拒绝
        s = {"x": {"module": "ICache", "port": "debug.out"},
             "y": {"module": "DCache", "port": "io.cpu.req.valid"}}
        with self.assertRaises(ClassifyError) as cm:
            classify(prop(s, "atomic", "Datapath"), self.h, self.reader)
        self.assertIn("一致性门拒绝", str(cm.exception))

    def test_atomic_without_module_rejected(self):
        # 信号分属多模块且声明 atomic 但未指明 module -> 拒绝
        with self.assertRaises(ClassifyError) as cm:
            classify(prop(S_CROSS_TILE, "atomic"), self.h, self.reader)
        self.assertIn("必须指明归属 module", str(cm.exception))

    def test_declared_module_conflict_rejected(self):
        # |S|==1 但声明归属与唯一宿主矛盾 -> 拒绝
        with self.assertRaises(ClassifyError) as cm:
            classify(prop(S_DCACHE_ONLY, "atomic", "ICache"),
                     self.h, self.reader)
        self.assertIn("唯一宿主", str(cm.exception))

    def test_composite_declared_but_atomic_ok(self):
        r = classify(prop(S_DCACHE_ONLY, "composite"), self.h, self.reader)
        self.assertEqual(r["derived"]["scope"], "atomic")

    def test_unknown_module_rejected(self):
        bad = {"x": {"module": "Foo", "port": "io.a"}}
        with self.assertRaises(ClassifyError):
            classify(prop(bad), self.h, self.reader)

    def test_missing_signals_rejected(self):
        with self.assertRaises(ClassifyError):
            classify({"id": "P1", "formula": "G(a)"}, self.h, self.reader)

    def test_remap_same_parent(self):
        # 已由 test_same_wire_two_views_atomic 覆盖合一重映射
        pass


class TestSubtreeMatch(unittest.TestCase):
    """连接侧比端口组更深 (A.g <-> B.q.x) 时的子信号匹配"""

    HIER2 = {
        "modules": [
            {"name": "Top"},
            {"name": "A", "inst": "a", "parent": "Top"},
            {"name": "B", "inst": "b", "parent": "Top"},
        ],
        "connections": [
            {"from": "A.g", "to": "B.q.x"}      # B 侧是子字段
        ],
    }

    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        p = Path(self.tmp) / "h.json"
        p.write_text(json.dumps(self.HIER2), encoding="utf-8")
        self.h = Hierarchy.load(str(p))
        self.reader = FakeReader()

    def test_subsignal_matches(self):
        # 信号 B.q.x.f 落在连接侧 B.q.x 子树内 -> 以 A 视角 g.f 表达
        s = {"p": {"module": "A", "port": "g.f"},
             "q": {"module": "B", "port": "q.x.f"}}
        r = classify(prop(s, "atomic", "A"), self.h, self.reader)
        self.assertEqual(r["derived"]["scope"], "atomic")
        self.assertEqual(r["derived"]["module"], "A")
        self.assertEqual(r["derived"]["signals"]["q"]["port"], "g.f")
        self.assertEqual(r["derived"]["signals"]["q"]["via"], "B.q.x.f")

    def test_equal_path_matches(self):
        # 信号与连接侧完全相等 -> 命中, 后缀空
        s = {"p": {"module": "A", "port": "g"},
             "q": {"module": "B", "port": "q.x"}}
        r = classify(prop(s, "atomic", "A"), self.h, self.reader)
        self.assertEqual(r["derived"]["scope"], "atomic")
        self.assertEqual(r["derived"]["signals"]["q"]["port"], "g")

    def test_wider_signal_maps_via_connection(self):
        # A.g(整 bundle) ≡ B.q.x 整个子树 -> 以 B 视角表达为 q.x
        s = {"p": {"module": "A", "port": "g"},
             "q": {"module": "B", "port": "q"}}
        r = classify(prop(s, "atomic", "B"), self.h, self.reader)
        self.assertEqual(r["derived"]["scope"], "atomic")
        self.assertEqual(r["derived"]["module"], "B")
        self.assertEqual(r["derived"]["signals"]["p"]["port"], "q.x")

    def test_sibling_subtree_unifiable_at_b(self):
        # A.g.f 与 B.q.y.f: 前者以 B 视角为 q.x.f, 与后者同在 B -> atomic
        s = {"p": {"module": "A", "port": "g.f"},
             "q": {"module": "B", "port": "q.y.f"}}
        r = classify(prop(s, "atomic", "B"), self.h, self.reader)
        self.assertEqual(r["derived"]["scope"], "atomic")
        self.assertEqual(r["derived"]["module"], "B")
        self.assertEqual(r["derived"]["signals"]["p"]["port"], "q.x.f")

    def test_disjoint_port_groups_composite(self):
        # p 的端口组 h 不在任何连接上, 与 B 无法合一 -> composite
        s = {"p": {"module": "A", "port": "h.f"},
             "q": {"module": "B", "port": "q.y.f"}}
        r = classify(prop(s, "composite"), self.h, self.reader)
        self.assertEqual(r["derived"]["scope"], "composite")


if __name__ == "__main__":
    unittest.main()
