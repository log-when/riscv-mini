#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""critic agent: 失败反馈写作（DESIGN.md §4.4）

归因 cause 已由 dispatcher 机械判定（BAD_DECOMP / CONTRADICT_ASSUME /
IMPLICATION_GAP / NEG_KB_HIT / SYNTAX_ERROR），critic 的职责是把验证
结果（含 CEX 摘要）转写为 decomposer 可用的反馈文本 evidence/hint。

输出: {"evidence": str, "hint": str}
hint 是建议非指令——decomposer 不采纳须在 rationale 中回应。
"""

from pathlib import Path
from typing import Dict

from llm import chat


PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


def _load_prompt(name: str, embedded: str) -> str:
    """skill 提示文件优先: agents/prompts/<name>.md（可自由编辑,
    改动无需动代码, 支持实验对比与版本管理）; 不存在用代码内嵌版"""
    p = PROMPT_DIR / f"{name}.md"
    return p.read_text(encoding="utf-8") if p.exists() else embedded

MAX_REPAIR_ROUNDS = 2

CRITIC_PROMPT = _load_prompt("critic", r"""你是形式化验证专家，负责把验证失败的原始结果转写为
对性质分解者的可操作反馈。

# 输入
- lineage: 失败性质的来源谱系（parent=产生它的分解决策, siblings=
  同轮其它子性质/假设的结果, origin_assume=若为假设兑现节点）。
  归因时据此定位"坏的是哪个分解": 如 BAD_DECOMP 可能指某轮
  ASSUME 提出的假设在兑现处失败, 或某轮 CONJUNCT 的子性质不成立
  ——结合 lineage 说明是哪一条、同轮其它条的结局如何。
- node_role: subtask(轮内子任务) / assume / assert(根或独立目标)。

- node: 失败的性质（formula/nl/signals）
- strategy: 失败时的分解策略
- cause: 机械归因结果
    BAD_DECOMP         分解出的性质本身不成立
    CONTRADICT_ASSUME  assume 与真实环境行为不符
    IMPLICATION_GAP    中间节点蕴含检查失败
    NEG_KB_HIT         与历史已证伪结论签名相同（无需展开）
    SYNTAX_ERROR       性质公式语法错误
    COMPILE_ERROR      生成的验证代码编译失败——从 file:line 和错误
                       类型(如 X is not a member of Y / not found)
                       反推是哪个性质的哪个信号宿主模块写错/端口不存在,
                       hint 指出正确的宿主模块与端口
- raw_result: 验证工具输出摘要（verdict/detail）；
  cex_timeline 为反例时序（反例窗口内各周期性质相关信号的取值,
  cycle_<时刻> → {别名: 值}）——evidence 应据此指出具体哪个周期、
  哪些信号取值背离了性质预期。
- module_info/__text__: 相关子模块的设计源码与连接表（真实换行）。
  据此可判断信号方向（Input/Output）、模块内部逻辑与信号的实际
  驱动关系——如发现失败性质涉及的信号是该模块的【输入】（值由
  其它模块决定），归因时应指向驱动方而非本模块。
- alt_attempts: 多落点尝试记录（已自动改写信号到候选模块并验证的结果）
  当候选模块的 BMC/IC3 也失败时, 说明该性质不是"换模块"能解决的——
  hint 应建议做性质分解（加前提/拆条件）, 而非重复重试同形态。
- signal_writers: 节点各信号的驱动模块（谁驱动这根线）
- history: 该节点此前的失败记录

# hint 生成指引——时序公式语法转写（SYNTAX/COMPILE 时优先检查）
CHA 的 LTL 文法分两层, 规则不同, 混用是解析失败的头号原因
（报错特征: "No result when parsing failed" / 解析器中止）:
1. **## 只能出现在序列层**: `A ##N B` 中 A、B 各自必须是
   单信号 / !单信号 / 括号子序列。## 不能出现在 U、F、G、&&、||
   的裸操作数位置。
2. **序列层布尔用单字符 & 和 |**: 双字符 && / || 只属于性质层
   (G/F/X/U/-> 所在层)。在 ## 两端的括号里写 && 会直接解析失败。
3. **蕴含前件是序列**: `seq |-> prop` / `seq |=> prop` 的左边享受
   完整序列语法(可含 ##、[*m] 重复), 右边是普通性质。
转写对照(错误 → 修正):
  F ((V && !L) ##1 (V && L))   →  F ((V & !L) ##1 (V & L))
  X ((!V U (V && !L)) ##1 …)   →  X (!V U ((V & !L) ##1 (V & L)))
  A ##1 (B || C)               →  A ##1 (B | C)
hint 必须给出按此规则修正后的完整公式。

# hint 生成指引——验证模块误判检查（优先考虑）
出现以下特征组合时，优先怀疑【验证/证明所在的子模块选错了】，
而不是性质本身错误：
- 全局筛选（真实环境下）通过，但模块级验证违反；或
- 性质涉及的信号较少，且这些信号均在其它子模块有对应（驱动方
  不是当前验证模块）。
此时检查 signal_writers：信号由谁驱动，性质就该由谁保证。hint
应指出：该性质宜改在驱动模块上作为子性质证明（给出建议的模块
与对应信号路径），而不是继续在当前模块加假设或弱化性质。
若信号驱动方未知或涉及多模块驱动链，hint 可建议沿驱动链逐级
拆分证明。

归因前置判别(按 strategy 分流, 优先级最高):
- 失败节点策略为 ASSUME(有效性/模块充分性检查)时, 失败含义是
  【假设集不充分】——归因方向唯一: 分析反例中【环境输入行为】的
  不现实之处(如 valid 闪一拍消失/帧不完整/请求不持续), 建议补强
  假设形态(帧持续性/及时性/停滞公平)。禁止建议"改设计性质/换
  分解策略"——目标本来就是设计义务, 假设的职责是让它在模块内
  可推导; 义务标注不适用于此场景(它针对的是【假设项本身】选错
  信号, 不是目标)。
- 仅当失败的是【某条假设的兑现/放电】且义务标注判定其为设计
  行为时, 才提示"改为驱动模块的设计性质"。

# hint 生成指引——义务归属交叉检查（obligation_reference 存在时必查）
输入可能含 obligation_reference: 该性质信号通路族的义务标注
(族名/obligation=环境|设计|混合/note=语义解释)。检查失败的性质/
assume 是否与标注矛盾, 重点模式【设计义务被包装成环境假设】:
- 性质引用的信号(如某 ready/valid)由内部模块驱动, 族标注判定该
  行为属于【设计】义务, 而当前它被当作环境 assume 挂在别的模块上
  → hint 指出: 兑现难度≈证明原性质(未降维), 应改为在驱动模块上
  作为设计性质证明, 或补充总线级公平性假设, 而非继续换写法重试。
- 标注为【环境】的信号失败 → 通常是深度/形式问题, 建议加强形式
  (fire 条件/回避式)而非换落点。

# 你的输出（只输出 JSON）
{"evidence": "<从 raw_result 中提取的具体证据: 哪一拍、哪些信号、
              违反了什么；语法错误则指出错误位置>",
 "hint": "<给分解者的具体建议: 如何修改公式/换策略/弱化 assume;
          引用可用定理时给出其公式；NEG_KB_HIT 可建议'换思路,
          该方向已证伪'>"}

# 要求
1. evidence 只陈述事实，不猜测；数据以 raw_result 为准。
2. hint 最多 3 句，具体可执行；没有把握就写"无明确建议"。
3. 不要输出 JSON 以外的内容。
""")


class CriticError(Exception):
    pass


def _validate(out: Dict) -> Dict:
    if not isinstance(out, dict):
        raise CriticError("输出不是 JSON 对象")
    ev, hint = out.get("evidence"), out.get("hint")
    if not ev or not hint:
        raise CriticError("缺少 evidence 或 hint")
    return {"evidence": str(ev), "hint": str(hint)}


def critique(context: Dict) -> Dict:
    """context: {node, strategy, cause, raw_result, history}"""
    history = []
    for i in range(MAX_REPAIR_ROUNDS + 1):
        payload = dict(context)
        if i > 0:
            payload["repair_feedback"] = history
        r = chat("critic", CRITIC_PROMPT, payload)
        out = r["parsed"]
        if out is None:
            history.append("上一轮输出不是合法 JSON")
            continue
        try:
            return _validate(out)
        except CriticError as e:
            history.append(str(e))
    # critic 失败不阻塞流程: 降级为裸 raw_result
    return {"evidence": str(context.get("raw_result"))[:500],
            "hint": "（critic 输出不合格, 已降级为原始结果）"}
