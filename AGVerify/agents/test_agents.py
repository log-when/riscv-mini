#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""decomposer/critic 单元测试: mock chat, 不发真实请求"""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import decomposer as dc
import critic as cr


def mock_chat_side_effect(responses):
    """依次返回给定 (parsed 或 None) 的 chat mock"""
    it = iter(responses)

    def fake(agent, prompt, payload, **kw):
        return {"parsed": next(it)}
    return fake


GOOD_CONJ = {
    "strategy": "CONJUNCT", "rationale": "r",
    "children": [
        {"id": "P1.1", "nl": "a", "formula": "G(x)",
         "signals": {"x": {"module": "ICache", "port": "io.a"}}},
        {"id": "P1.2", "nl": "b", "formula": "F(y)",
         "signals": {"y": {"module": "ICache", "port": "io.b"}}}],
    "assumes": []}

GOOD_ASSUME = {
    "strategy": "ASSUME", "rationale": "r", "children": [],
    "assumes": [
        {"id": "A1", "nl": "a", "formula": "G(p -> X q)",
         "signals": {"p": {"module": "ICache", "port": "io.nasti.ar.fire"},
                     "q": {"module": "ICache", "port": "io.nasti.r.valid"}},
         "target_module": "ICache"}]}


class TestValidate(unittest.TestCase):
    def test_good_conjunct(self):
        out = dc.validate_decision(GOOD_CONJ)
        self.assertEqual(out["strategy"], "CONJUNCT")
        self.assertEqual(len(out["children"]), 2)

    def test_good_assume(self):
        out = dc.validate_decision(GOOD_ASSUME)
        self.assertEqual(len(out["assumes"]), 1)

    def test_mixed_rejected(self):
        bad = dict(GOOD_CONJ); bad["assumes"] = GOOD_ASSUME["assumes"]
        with self.assertRaises(dc.DecomposeError):
            dc.validate_decision(bad)

    def test_locked_rejects_assume(self):
        with self.assertRaises(dc.DecomposeError):
            dc.validate_decision(GOOD_ASSUME, locked=True)

    def test_undeclared_atom_rejected(self):
        bad = dict(GOOD_CONJ)
        bad["children"][0]["formula"] = "G(x && zzz)"
        with self.assertRaises(dc.DecomposeError) as cm:
            dc.validate_decision(bad)
        self.assertIn("zzz", str(cm.exception))

    def test_children_count_bounds(self):
        bad = dict(GOOD_CONJ)
        bad["children"] = [GOOD_CONJ["children"][0]]
        with self.assertRaises(dc.DecomposeError):
            dc.validate_decision(bad)

    def test_missing_rationale(self):
        bad = dict(GOOD_CONJ); bad["rationale"] = ""
        with self.assertRaises(dc.DecomposeError):
            dc.validate_decision(bad)


class TestAntiDegenerate(unittest.TestCase):
    def _dec(self, children, parent="F response"):
        d = {"strategy": "CONJUNCT", "rationale": "r", "children": children}
        return dc.validate_decision(d, parent_formula=parent)

    def _sig(self, name):
        return {"module": "ICache", "port": "io.a"}

    def test_pure_signal_allowed(self):
        # 纯信号可能有意义（如 assume "disWrite"）, 不作为退化
        out = self._dec([{"formula": "response", "signals": {"response": self._sig("x")}},
                         {"formula": "F b", "signals": {"b": self._sig("y")}}])
        self.assertEqual(len(out["children"]), 2)

    def test_same_as_parent_rejected(self):
        with self.assertRaises(dc.DecomposeError) as cm:
            self._dec([{"formula": "F response", "signals": {"response": self._sig("x")}},
                       {"formula": "F b", "signals": {"b": self._sig("y")}}],
                      parent="F response")
        self.assertIn("原地打转", str(cm.exception))

    def test_tautology_rejected(self):
        with self.assertRaises(dc.DecomposeError) as cm:
            self._dec([{"formula": "G(a -> a)", "signals": {"a": self._sig("x")}},
                       {"formula": "b || !b", "signals": {"b": self._sig("y")}}])
        self.assertIn("永真式", str(cm.exception))

    def test_duplicate_child_rejected(self):
        with self.assertRaises(dc.DecomposeError) as cm:
            self._dec([{"formula": "G(a)", "signals": {"a": self._sig("x")}},
                       {"formula": "G (a)", "signals": {"a": self._sig("x")}}])
        self.assertIn("重复", str(cm.exception))

    def test_normal_passes(self):
        out = self._dec([{"formula": "G(a -> F b)",
                          "signals": {"a": self._sig("x"), "b": self._sig("y")}},
                         {"formula": "F c", "signals": {"c": self._sig("z")}}])
        self.assertEqual(len(out["children"]), 2)

    def test_disable_switch(self):
        dc.ANTI_DEGENERATE = False
        try:
            out = self._dec([{"formula": "a -> a", "signals": {"a": self._sig("x")}},
                             {"formula": "F b", "signals": {"b": self._sig("y")}}])
            self.assertEqual(len(out["children"]), 2)
        finally:
            dc.ANTI_DEGENERATE = True


class TestAssertKind(unittest.TestCase):
    def _sig(self):
        return {"a": {"module": "ICache", "port": "io.a"}}

    def test_global_strips_outer_g(self):
        out = dc.validate_decision({
            "strategy": "CONJUNCT", "rationale": "r",
            "children": [
                {"formula": "G F a", "assert_kind": "global", "signals": self._sig()},
                {"formula": "F b", "assert_kind": "global",
                 "signals": {"b": {"module": "ICache", "port": "io.b"}}}]})
        self.assertEqual(out["children"][0]["formula"], "F a")

    def test_once_keeps_formula(self):
        out = dc.validate_decision({
            "strategy": "CONJUNCT", "rationale": "r",
            "children": [
                {"formula": "G init_done", "assert_kind": "once",
                 "signals": {"init_done": {"module": "ICache", "port": "io.a"}}},
                {"formula": "F b", "assert_kind": "global",
                 "signals": {"b": {"module": "ICache", "port": "io.b"}}}]})
        self.assertEqual(out["children"][0]["formula"], "G init_done")
        self.assertEqual(out["children"][0]["assert_kind"], "once")

    def test_default_is_global(self):
        out = dc.validate_decision({
            "strategy": "CONJUNCT", "rationale": "r",
            "children": [
                {"formula": "F a", "signals": self._sig()},
                {"formula": "F b", "signals": {"b": {"module": "ICache", "port": "io.b"}}}]})
        self.assertEqual(out["children"][0]["assert_kind"], "global")

    def test_bad_kind_rejected(self):
        with self.assertRaises(dc.DecomposeError):
            dc.validate_decision({
                "strategy": "CONJUNCT", "rationale": "r",
                "children": [
                    {"formula": "F a", "assert_kind": "always", "signals": self._sig()},
                    {"formula": "F b", "signals": {"b": {"module": "ICache", "port": "io.b"}}}]})


class TestDecomposeLoop(unittest.TestCase):
    def _ctx(self, locked=False):
        return {"node": {"formula": "G(a -> F b)"},
                "constraints": {"locked": locked}}

    def test_success_first_try(self):
        with mock.patch.object(dc, "chat",
                               side_effect=mock_chat_side_effect([GOOD_CONJ])):
            out = dc.decompose(self._ctx())
        self.assertEqual(out["strategy"], "CONJUNCT")

    def test_repair_then_success(self):
        with mock.patch.object(dc, "chat",
                               side_effect=mock_chat_side_effect(
                                   [None, {"strategy": "BAD"}, GOOD_CONJ])):
            out = dc.decompose(self._ctx())
        self.assertEqual(out["strategy"], "CONJUNCT")

    def test_exhaust_repair_raises(self):
        bad = {"strategy": "CONJUNCT", "rationale": "r",
               "children": [{"formula": "G(x)",
                             "signals": {"x": {"module": "M", "port": "p"}}}]}
        with mock.patch.object(dc, "chat",
                               side_effect=mock_chat_side_effect(
                                   [bad, bad, bad])):
            with self.assertRaises(dc.DecomposeError):
                dc.decompose(self._ctx())


class TestCritic(unittest.TestCase):
    CTX = {"node": {"formula": "G(a)"},
           "strategy": "ASSUME", "cause": "CONTRADICT_ASSUME",
           "raw_result": {"verdict": "FAIL", "detail": "violation @3"},
           "history": []}

    def test_success(self):
        with mock.patch.object(cr, "chat",
                               side_effect=mock_chat_side_effect(
                                   [{"evidence": "e", "hint": "h"}])):
            out = cr.critique(self.CTX)
        self.assertEqual(out, {"evidence": "e", "hint": "h"})

    def test_degrade_on_bad_output(self):
        with mock.patch.object(cr, "chat",
                               side_effect=mock_chat_side_effect(
                                   [None, "junk", None])):
            out = cr.critique(self.CTX)
        self.assertIn("降级", out["hint"])


if __name__ == "__main__":
    unittest.main()
