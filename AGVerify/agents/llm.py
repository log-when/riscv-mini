#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LLM 调用层（直接 API, OpenAI 兼容接口）

配置来源（优先级: 环境变量 > AGVerify/.env > 内置默认）:
  LLM_BASE_URL   API 地址（如 https://api.xxx.com/v1）
  LLM_API_KEY    密钥
  LLM_MODEL      模型名
  LLM_TIMEOUT    单次请求超时秒数（默认 300）
  LLM_PROXY      HTTP(S) 代理（如 http://127.0.0.1:7890; 留空不走代理）
  LLM_TEMPERATURE 采样温度（默认 0.8; 分解重试需要发散探索）

.env 格式（KEY=VALUE, # 注释）:
  LLM_BASE_URL=...
  LLM_API_KEY=...
  LLM_MODEL=...

审计: 每次调用记录到独立子文件夹
  AGVerify/results/llm_calls/<时间戳>_<agent>/
    input.json    完整请求（messages/参数）
    output.json   原始返回 + 解析后结果
    meta.json     agent/模型/耗时/成功与否/token 数（如返回）
"""

import json
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests

AGV = Path(__file__).resolve().parents[1]
ENV_FILE = Path(__file__).resolve().parent / ".env"   # agents/.env
CALL_DIR = AGV / "results" / "llm_calls"


def set_call_dir(path):
    """由 dispatcher 设置本次运行的审计子目录（按运行归档）"""
    global CALL_DIR
    CALL_DIR = Path(path)

_DEFAULTS = {"LLM_BASE_URL": "", "LLM_API_KEY": "", "LLM_MODEL": "",
             "LLM_TIMEOUT": "300", "LLM_PROXY": "",
             "LLM_TEMPERATURE": "0.8", "LLM_MAX_TOKENS": "8192"}


def load_env() -> Dict[str, str]:
    """环境变量 > .env 文件 > 默认值"""
    cfg = dict(_DEFAULTS)
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k in _DEFAULTS:
                cfg[k] = v
    for k in cfg:                       # 环境变量优先
        cfg[k] = os.environ.get(k, cfg[k])
    return cfg


class LLMError(Exception):
    pass


def chat(agent: str,
         system_prompt: str,
         user_payload: Dict,
         history: Optional[List[Dict]] = None,
         json_mode: bool = True,
         max_retries: int = 2) -> Dict:
    """一次 LLM 调用。返回 {"content": str, "parsed": Any|None, ...}

    agent: 调用方标识（decomposer/critic/...）, 用于审计子文件夹命名
    user_payload: 业务上下文（dict, 自动 json 序列化进 user 消息）
    history: 可选的多轮历史 [{"role","content"}, ...]
    json_mode: 要求模型返回 JSON（提示词追加约束 + 本地提取）
    """
    cfg = load_env()
    if not (cfg["LLM_BASE_URL"] and cfg["LLM_API_KEY"] and cfg["LLM_MODEL"]):
        raise LLMError(
            "LLM 配置缺失: 请设置环境变量或在 AGVerify/.env 中填写 "
            "LLM_BASE_URL / LLM_API_KEY / LLM_MODEL")

    # 挂钟护栏: requests 的 read-timeout 按单次 socket read 计,
    # 服务端零星字节即可无限续命(慢速滴注挂死, 实测1小时+)。
    # SIGALRM 强制总限(单线程安全), 超限抛 LLMError 交给上层重试。
    import signal as _signal

    class _WallClockAlarm(Exception):
        pass

    _deadline = max(600, 3 * int(cfg["LLM_TIMEOUT"]))

    def _on_alarm(signum, frame):
        raise _WallClockAlarm()

    _old_hdl = _signal.signal(_signal.SIGALRM, _on_alarm)
    _signal.alarm(_deadline)
    try:
        return _chat_inner(agent, system_prompt, user_payload, history,
                           json_mode, max_retries, cfg)
    except _WallClockAlarm:
        raise LLMError(
            f"LLM 调用挂钟超限 {_deadline}s (疑似服务端挂死连接)")
    finally:
        _signal.alarm(0)
        _signal.signal(_signal.SIGALRM, _old_hdl)


def _chat_inner(agent, system_prompt, user_payload, history, json_mode,
                max_retries, cfg):
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    # __text__: {标题: 文本} —— 以真实换行追加(不经 JSON 转义),
    # 用于模块源码等需要保留换行结构的内容
    payload = dict(user_payload)
    text_sections = payload.pop("__text__", None) or {}
    user_content = json.dumps(payload, ensure_ascii=False, indent=2)
    for title, body in text_sections.items():
        user_content += f"\n\n## {title}\n{body}"
    if json_mode:
        user_content += ("\n\n请只输出一个 JSON 对象，不要包含其它文本"
                         "或 markdown 代码块标记。")
    messages.append({"role": "user", "content": user_content})
    _readable = "\n\n".join(f"===== [{m['role']}] =====\n{m['content']}"
                             for m in messages)
    _last_readable = (f"model: {cfg['LLM_MODEL']}\n\n"
                      + "\n\n".join(f"===== [{m['role']}] =====\n{m['content']}"
                                     for m in messages))

    body = {"model": cfg["LLM_MODEL"], "messages": messages,
            "temperature": float(cfg["LLM_TEMPERATURE"])}
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    call_id = time.strftime("%Y%m%d_%H%M%S") + f"_{agent}"
    out_dir = CALL_DIR / call_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "input.json").write_text(
        json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "input.readable.txt").write_text(
        _last_readable, encoding="utf-8")

    gpugeek_style = cfg["LLM_BASE_URL"].rstrip("/").endswith("/predictions")

    if gpugeek_style:
        # gpugeek 原生 API: POST /predictions, body={model, input:{prompt}},
        # 流式返回; prompt 由 system+user 拼接
        url = cfg["LLM_BASE_URL"].rstrip("/")
        prompt = "\n\n".join(m["content"] for m in messages)
        body = {"model": cfg["LLM_MODEL"],
                "input": {"prompt": prompt,
                          "temperature": float(cfg["LLM_TEMPERATURE"]),
                          "max_tokens": int(cfg.get("LLM_MAX_TOKENS", "8192"))}}
        return _post_gpugeek(cfg, url, body, agent, json_mode)

    url = cfg["LLM_BASE_URL"].rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {cfg['LLM_API_KEY']}",
               "Content-Type": "application/json"}

    last_err = None
    for attempt in range(max_retries + 1):
        t0 = time.time()
        try:
            proxies = None
            if cfg.get("LLM_PROXY"):
                proxies = {"http": cfg["LLM_PROXY"],
                           "https": cfg["LLM_PROXY"]}
            resp = requests.post(
                url, headers=headers, json=body, proxies=proxies,
                timeout=int(cfg["LLM_TIMEOUT"]))
            elapsed = round(time.time() - t0, 2)
            if resp.status_code != 200:
                raise LLMError(f"HTTP {resp.status_code}: {resp.text[:300]}")
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            parsed = extract_json(content) if json_mode else None
            usage = data.get("usage", {})
            meta = {"agent": agent, "model": cfg["LLM_MODEL"],
                    "elapsed_sec": elapsed, "attempt": attempt,
                    "usage": usage,
                    "json_extracted": parsed is not None if json_mode else None}
            (out_dir / "output.json").write_text(
                json.dumps({"raw": data, "content": content,
                            "parsed": parsed}, ensure_ascii=False, indent=2),
                encoding="utf-8")
            (out_dir / "meta.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=2),
                encoding="utf-8")
            return {"content": content, "parsed": parsed,
                    "elapsed_sec": elapsed, "call_dir": str(out_dir),
                    "usage": usage}
        except Exception as e:            # 网络/HTTP/解析错误 → 重试
            last_err = e
            time.sleep(2 * (attempt + 1))
    meta = {"agent": agent, "model": cfg["LLM_MODEL"],
            "error": str(last_err)}
    (out_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    raise LLMError(f"LLM 调用失败（已重试 {max_retries} 次）: {last_err}")


def _post_gpugeek(cfg, url, body, agent, json_mode):
    """gpugeek 原生 /predictions 调用（非流式: 流式模式服务端有
    生成不回传的 bug, 非流式返回完整 output 数组）。"""
    call_id = time.strftime("%Y%m%d_%H%M%S") + f"_{agent}"
    out_dir = CALL_DIR / call_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "input.json").write_text(
        json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    # input.readable.txt 已在 chat() 统一写入(带 system/user 分段)
    headers = {"Authorization": f"Bearer {cfg['LLM_API_KEY']}",
               "Content-Type": "application/json"}
    proxies = ({"http": cfg["LLM_PROXY"], "https": cfg["LLM_PROXY"]}
               if cfg.get("LLM_PROXY") else None)
    t0 = time.time()
    last_err = None
    resp = None
    empty_retries = 0
    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=body,
                                 proxies=proxies, stream=False,
                                 timeout=int(cfg["LLM_TIMEOUT"]))
            # 空输出(服务端截断/丢流) → 重试
            _d = resp.json()
            _o = _d.get("output")
            _c = "".join(str(x) for x in _o) if isinstance(_o, list) else str(_o or "")
            if _c.strip() or attempt == 2:
                break
            empty_retries += 1
            time.sleep(3)
        except Exception as e:
            last_err = e
            time.sleep(5)
    elapsed = round(time.time() - t0, 2)
    if resp is None:
        meta = {"agent": agent, "model": cfg["LLM_MODEL"],
                "elapsed_sec": elapsed, "error": f"{type(last_err).__name__}: {last_err}"}
        (out_dir / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        raise LLMError(f"gpugeek 调用失败(已重试): {last_err}")
    if resp.status_code != 200:
        meta = {"agent": agent, "model": cfg["LLM_MODEL"],
                "elapsed_sec": elapsed,
                "error": f"HTTP {resp.status_code}: {resp.text[:300]}"}
        (out_dir / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        raise LLMError(f"HTTP {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    out = data.get("output")
    content = "".join(str(x) for x in out) if isinstance(out, list) else str(out or "")
    metrics = data.get("metrics") or {}
    raw_lines = [json.dumps({k: data.get(k) for k in
                             ("status", "error", "metrics")},
                            ensure_ascii=False)]
    parsed = extract_json(content) if json_mode else None
    (out_dir / "output.json").write_text(
        json.dumps({"content": content, "parsed": parsed,
                    "raw_lines_sample": raw_lines},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "meta.json").write_text(
        json.dumps({"agent": agent, "model": cfg["LLM_MODEL"],
                    "elapsed_sec": elapsed, "style": "gpugeek",
                    "json_extracted": parsed is not None if json_mode else None},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    return {"content": content, "parsed": parsed, "elapsed_sec": elapsed,
            "call_dir": str(out_dir), "usage": {}}


def extract_json(text: str):
    """从模型返回中提取 JSON（容忍 markdown 代码块/前后杂文）"""
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # 兜底: 首个平衡的大括号块
    depth, start = 0, None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    return json.loads(text[start:i + 1])
                except Exception:
                    start = None
    return None
