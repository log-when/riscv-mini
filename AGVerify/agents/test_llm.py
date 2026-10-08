#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""llm.py 单元测试: mock HTTP, 不发真实请求; 验证配置加载/审计落盘/JSON 提取"""
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import llm


class TestLoadEnv(unittest.TestCase):
    def test_defaults_when_no_env(self):
        with mock.patch.object(llm, "ENV_FILE", Path("/nonexistent")):
            with mock.patch.dict("os.environ", {}, clear=True):
                cfg = llm.load_env()
        self.assertEqual(cfg["LLM_TIMEOUT"], "300")
        self.assertEqual(cfg["LLM_BASE_URL"], "")

    def test_env_file_and_os_override(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / ".env"
            f.write_text('LLM_BASE_URL=https://a/v1\n'
                         'LLM_API_KEY="k1"\n'
                         'LLM_MODEL=m1\n', encoding="utf-8")
            with mock.patch.object(llm, "ENV_FILE", f):
                with mock.patch.dict("os.environ", {}, clear=True):
                    cfg = llm.load_env()
                    self.assertEqual(cfg["LLM_MODEL"], "m1")
                    self.assertEqual(cfg["LLM_API_KEY"], "k1")
                # 环境变量优先于 .env
                with mock.patch.dict("os.environ", {"LLM_MODEL": "m2"}):
                    cfg = llm.load_env()
                    self.assertEqual(cfg["LLM_MODEL"], "m2")


class FakeResp:
    def __init__(self, payload, status=200):
        self._p, self.status_code = payload, status
        self.text = json.dumps(payload)

    def json(self):
        return self._p


def ok_payload(content):
    return {"choices": [{"message": {"content": content}}],
            "usage": {"total_tokens": 42}}


class TestChatAudit(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        self.cfg = {"LLM_BASE_URL": "https://x/v1", "LLM_API_KEY": "k",
                    "LLM_MODEL": "m", "LLM_TIMEOUT": "5",
                    "LLM_TEMPERATURE": "0.8", "LLM_PROXY": ""}

    def _chat(self, content):
        with mock.patch.object(llm, "load_env", return_value=self.cfg), \
             mock.patch.object(llm, "CALL_DIR", Path(self.tmp)), \
             mock.patch("llm.requests.post",
                        return_value=FakeResp(ok_payload(content))):
            return llm.chat("decomposer", "sys", {"node": "P1"})

    def test_audit_files_written(self):
        r = self._chat('{"strategy": "CONJUNCT"}')
        self.assertEqual(r["parsed"]["strategy"], "CONJUNCT")
        d = Path(r["call_dir"])
        for f in ("input.json", "output.json", "meta.json"):
            self.assertTrue((d / f).exists(), f)
        meta = json.loads((d / "meta.json").read_text())
        self.assertEqual(meta["agent"], "decomposer")
        self.assertEqual(meta["model"], "m")
        self.assertGreaterEqual(meta["elapsed_sec"], 0)
        self.assertEqual(meta["usage"]["total_tokens"], 42)
        inp = json.loads((d / "input.json").read_text())
        self.assertEqual(inp["model"], "m")
        self.assertEqual(len(inp["messages"]), 2)

    def test_json_extraction_variants(self):
        # 纯 JSON / markdown 块 / 前后杂文
        r1 = self._chat('{"a": 1}')
        r2 = self._chat('```json\n{"a": 2}\n```')
        r3 = self._chat('结果如下：{"a": 3} 请查收')
        self.assertEqual([r["parsed"]["a"] for r in (r1, r2, r3)],
                         [1, 2, 3])

    def test_missing_config_raises(self):
        with mock.patch.object(
                llm, "load_env",
                return_value=dict(llm._DEFAULTS)), \
             mock.patch.object(llm, "CALL_DIR", Path(self.tmp)):
            with self.assertRaises(llm.LLMError):
                llm.chat("x", "s", {})


class TestExtractJson(unittest.TestCase):
    def test_unextractable(self):
        self.assertIsNone(llm.extract_json("not json at all"))
        self.assertIsNone(llm.extract_json("{broken"))


if __name__ == "__main__":
    unittest.main()
