#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rtl_compress: 目标性质感知的 RTL 压缩(供 decomposer 的 ctx)

输入: 目标性质 + 全部模块源码 → LLM 压缩为结构化摘要;
输出经【名字校验】(摘要中的标识符必须在源码中出现), 不通过的
标识符自动剔除并标注。缓存按 (性质, 源码指纹); 多轮语法错误时
以出错表达式为反馈重新压缩(invalidate + regenerate)。
"""
import hashlib
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from llm import chat  # noqa: E402

CACHE_PATH = _HERE.parent / 'out' / 'rtl_compress' / 'cache.json'

PROMPT = """你是 RTL 压缩专家。输入是待验证的时序性质和 SoC 各模块的
Chisel 源码。任务: 把源码压缩成 decomposer(性质分解 LLM)可直接使用的
结构化摘要——保留它与该性质相关的全部【可引用信息】, 删除无关实现细节。

输出 JSON:
{"digest": "markdown 摘要, 按下列结构组织"}

摘要结构要求(每个模块一节):
## <模块名> (inst=<实例名>, src=<文件>)
### 端口表
- io.<路径> : 方向 : 语义一句话
### 状态机(若有)
- 状态枚举【逐字照抄源码中的准确拼写】及编码
- 转移条件表: 条件(用源码中的信号名) → 目标状态
### 关键寄存器/内部信号
- <名字>: 含义(计数器/valid寄存器/缓存阵列...)
### 协议行为要点
- 握手时序/公平性/阻塞条件(与性质相关的部分)
### 可证性质提示
- 模块内显然成立的不变式/活性(可选)

复杂逻辑补充源码: 当某段逻辑难以用摘要表准确表达时(嵌套 when 的
握手、多计数器交互、tricky 的 valid/ready 组合), 允许【原样摘抄】
该段源码放在 ```scala 代码块中, 配一句话说明它为什么关键。
摘抄的代码同样受标识符校验保护。

硬性规则:
1. 所有信号/状态/寄存器名必须与源码逐字一致(禁止缩写/改拼);
2. 与性质无关的纯数据通路细节(位拼接/移位等)可删;
3. 总长控制在源码的 1/5 以内(含摘抄的代码块);
4. 摘要中出现的每个标识符都必须能在源码中找到(会被程序校验)。"""


def _fingerprint(formula: str, sources: dict) -> str:
    h = hashlib.md5()
    h.update(formula.encode('utf-8'))
    for name in sorted(sources):
        h.update(name.encode('utf-8'))
        h.update(hashlib.md5(sources[name].encode('utf-8')).digest())
    return h.hexdigest()[:16]


def _load_cache() -> dict:
    try:
        if CACHE_PATH.exists():
            return json.loads(CACHE_PATH.read_text(encoding='utf-8'))
    except Exception:
        pass
    return {}


def _save_cache(c: dict):
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(json.dumps(c, ensure_ascii=False, indent=1),
                              encoding='utf-8')
    except Exception:
        pass


_ID_RE = re.compile(r'[A-Za-z_][A-Za-z0-9_]{2,}')
_STOP = {'the', 'and', 'for', 'not', 'with', 'src', 'inst', 'io', 'valid',
         'ready', 'bits', 'data', 'addr', 'state', 'true', 'false', 'None',
         'mark', 'CPU', 'response', 'writeback', 'read', 'write', 'fire',
         'last', 'mask', 'hit', 'miss', 'refill', 'burst', 'clean', '若', '有', '及', '和',
         '与', '或', '的', '中', '在'}


def _validate(digest: str, sources: dict) -> tuple:
    """摘要中的标识符必须出现在源码。返回 (清洗后摘要, 被剔标识符)"""
    corpus = '\n'.join(sources.values())
    bad = []
    for m in _ID_RE.finditer(digest):
        tok = m.group(0)
        if tok in _STOP or tok in bad:
            continue
        if tok not in corpus:
            bad.append(tok)
    cleaned = digest
    for b in bad:
        cleaned = cleaned.replace(b, '<已剔除:{}未知名>'.format(b))
    return cleaned, bad


def get_digest(formula: str, sources: dict,
               error_examples: list = None) -> dict:
    """→ {"digest": str, "violations": [...], "key": str}
    命中缓存返回缓存; error_examples 非空时强制重新生成并反馈。"""
    key = _fingerprint(formula, sources)
    cache = _load_cache()
    if not error_examples and key in cache:
        return dict(cache[key], key=key, cached=True)
    payload = {
        'formula': formula,
        'error_feedback': error_examples or [],
        '__text__': {
            '模块源码({})'.format(len(sources)):
            '\n\n'.join('===== {} =====\n{}'.format(k, v)
                        for k, v in sorted(sources.items()))
        },
    }
    r = chat('rtl_compress', PROMPT, payload, json_mode=True)
    parsed = r.get('parsed')
    if not parsed or not parsed.get('digest'):
        raise ValueError('rtl_compress 输出异常: {}'
                         .format(str(r.get('content'))[:200]))
    cleaned, bad = _validate(parsed['digest'], sources)
    entry = {'digest': cleaned, 'violations': bad}
    cache[key] = entry
    _save_cache(cache)
    # 可读落盘(drafts): 带性质/指纹/违规名头部
    try:
        ddir = _HERE.parent / 'out' / 'drafts'
        ddir.mkdir(parents=True, exist_ok=True)
        head = ('# RTL 压缩摘要\n- 性质: {}\n- 指纹: {}\n'
                '- 名字校验违规(已剔除): {}\n'
                '- 反馈样本: {}\n\n'.format(
                    formula, key, bad or '无',
                    len(error_examples or [])))
        (ddir / ('rtl_digest_{}.md'.format(key))).write_text(
            head + cleaned, encoding='utf-8')
    except Exception:
        pass
    return dict(entry, key=key, cached=False)


def invalidate(formula: str, sources: dict):
    key = _fingerprint(formula, sources)
    cache = _load_cache()
    cache.pop(key, None)
    _save_cache(cache)
