#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cha_verify 单元测试: 只测文件生成与日志解析, 不跑 sbt"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cha_verify import (TEST_FILE, build_test_file, gen_signal_lines,
                        parse_verify_log)

BMC_PASS = """chaAssertStmt: ! G (({p1}))
... [info] ICacheProp
[info] - should pass
[info] All tests passed.
[success] Total time: 95 s"""

IC3_PASS = """chaAssertStmt: ! G (({p1}))
All properties can be proven!
[info] All tests passed."""

BMC_FAIL = """[info] - should pass *** FAILED ***
[info]   chiseltest.formal.FailedBoundedCheckException: [ICacheProp] found an assertion violation 3 steps after reset!"""

IC3_FAIL = """java.lang.RuntimeException: Properties are violated, but rIC3 does not generate valid counter-examples, please try other backends"""

COMPILE_ERR = """[error] /path/TileTest.scala:66: not found: value io_icache_typo
[error]  val s0 = io.icache.typo.signal
[error] (Test / compileIncremental) Compilation failed"""


class TestParse(unittest.TestCase):
    def test_bmc_pass(self):
        self.assertEqual(parse_verify_log(BMC_PASS)["verdict"], "PASS")

    def test_ic3_pass(self):
        self.assertEqual(parse_verify_log(IC3_PASS)["verdict"], "PASS")

    def test_bmc_fail(self):
        r = parse_verify_log(BMC_FAIL)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("第 3 拍", r["detail"])

    def test_ic3_fail_no_cex(self):
        r = parse_verify_log(IC3_FAIL)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("不产生反例", r["detail"])

    def test_compile_error(self):
        self.assertEqual(parse_verify_log(COMPILE_ERR)["verdict"], "ERROR")


class TestGenerate(unittest.TestCase):
    def test_build_icache(self):
        signals = [("req", "io.cpu.req.valid", 20),
                   ("resp", "io.cpu.resp.valid", 21)]
        build_test_file("ICache", signals, ["F nastiReadReqReady"],
                        "G(req -> F resp)", mode="bmc", bound=15)
        text = TEST_FILE.read_text()
        self.assertIn("val req = io.cpu.req.valid", text)
        self.assertIn("SignalName(req,20)", text)
        self.assertIn('chaAssume(this, "F nastiReadReqReady")', text)
        self.assertIn('chaAssert(this, "G(req -> F resp)")', text)
        # ICache verify 行未注释, 其它模块注释
        self.assertIn('verify(new AGICacheProp', text)
        icache_blk = text.split('behavior of "ICache"')[1][:200]
        self.assertNotIn("//   verify", icache_blk)
        ctrl_blk = text.split('behavior of "Control"')[1][:200]
        self.assertIn("//     verify", ctrl_blk)
        self.assertIn("BoundedCheck(15), PonoEngineAnnotation", text)
        # 目标类含 assert, 非目标类干净
        self.assertEqual(text.count("chaAssert"), 1)

    def test_build_ic3_mode(self):
        build_test_file("Control", [("k", "io.inst_kill", 1)],
                        [], "G(k)", mode="ic3", bound=30)
        text = TEST_FILE.read_text()
        self.assertIn("Ic3Check(30), RIC3EngineAnnotation", text)

    def test_signal_lines(self):
        lines = gen_signal_lines([("a", "io.x", 1)])
        self.assertEqual(lines, ["val a = io.x", "SignalName(a,1)"])


if __name__ == "__main__":
    unittest.main()
