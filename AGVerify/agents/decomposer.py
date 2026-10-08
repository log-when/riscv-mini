#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""decomposer agent: 性质分解决策（DESIGN.md §4.1）

输入上下文（主循环组装）:
  node          当前节点（formula/nl/signals/derived）
  module_info   相关模块接口摘要
  kb            可用定理摘要（提示层）
  neg_kb        已证伪结论摘要
  history       本节点失败历史（截断）
  constraints   {locked: bool}（兑现节点禁 ASSUME）

输出（严格 JSON）:
  CONJUNCT: {"strategy": "CONJUNCT", "rationale": str,
             "children": [{"id","nl","formula","signals"}, ...]}
  ASSUME:   {"strategy": "ASSUME", "rationale": str,
             "assumes": [{"id","nl","formula","signals",
                          "target_module"}, ...]}
校验失败 → 错误回炉重试（默认 2 次）。
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

from llm import chat


PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


def _load_prompt(name: str, embedded: str) -> str:
    """skill 提示文件优先: agents/prompts/<name>.md（可自由编辑,
    改动无需动代码, 支持实验对比与版本管理）; 不存在用代码内嵌版"""
    p = PROMPT_DIR / f"{name}.md"
    return p.read_text(encoding="utf-8") if p.exists() else embedded

MAX_REPAIR_ROUNDS = 2

# 可选配置（AGVerify/config.json）
import json as _json
_cfg_file = Path(__file__).resolve().parents[1] / "config.json"
_cfg = {"anti_degenerate": True}
if _cfg_file.exists():
    _cfg.update(_json.loads(_cfg_file.read_text(encoding="utf-8")))
ANTI_DEGENERATE = _cfg["anti_degenerate"]

DECOMPOSER_PROMPT = _load_prompt("decomposer", r"""你是形式化验证专家，负责 assume-guarantee 组合验证中的性质分解。

# 你的任务
对一个待证明的时序性质，选择唯一一种分解策略。
user 消息中标注为「待验证性质(当前分解目标, node)」的字段即本次
要分解的性质（assert_kind 说明其语义），其余字段是辅助上下文。

## 假设保证策略
（一）确定分解策略。判断目标性质的成立是否依赖当前子模块自身的
行为，还是完全由其它子模块的行为保证。

**具体分析方法（引导思维链）**：

先分析因果关系，再追踪结论信号：

**步骤 1：识别因果结构**
- 性质是否有前提（如 `p -> q`、`p -> F q` 等）？
  - **有前提**：前提信号是什么？结论信号是什么？
  - **无前提**（如 `F p`、`G p` 等无条件形式）：性质中出现的信号
    本身即为结果信号（无需分析前提）

**步骤 2：追踪结论信号在当前模块中的角色**
- 若结论信号由当前模块的**内部逻辑驱动**（在源码中被赋值/修改），
  则性质的成立依赖当前模块的行为 → 倾向 ASSUME
- 若结论信号由**其它模块驱动**（当前模块只是转发/观察），
  则性质可拆分到驱动方模块分别证明 → 倾向 CONJUNCT

**步骤 3（可选中间输出）**：在 rationale 中先写出你的分析：
  "结论信号 X 由 [当前/其它] 模块驱动，因为 [源码依据]，
   因此性质成立 [依赖/不依赖] 当前模块行为，选择 [策略]"。
  这有助于检验你的判断是否正确。

- 前者（依赖当前模块行为）：优先考虑假设引入（ASSUME），为当前模块引入
  环境假设后在模块内完成证明；
- 后者（完全由其它模块保证）：优先考虑合取分解（CONJUNCT），把性质拆分到
  相关子模块上分别证明。

（二）应用策略时注意。
- 假设引入的约束要适度：既要约束掉不合法的输入行为，保证目标性质
  可证；又要避免约束过紧，排除掉环境中合法的行为路径（过强的假设
  无法在驱动模块处兑现）。
- 合取分解要顺着信号通路分解：分析当前性质中的信号由哪些其它
  子模块驱动，注意信号往往由多个子模块构成的驱动链共同作用；
  结合通路分析决定性质如何拆分。
- 分解子性质时把前提条件想完整：子性质成立是由什么导致的？
  将整条推理链（前提如何传导到结论）都纳入分解，不要只盯着
  最终结果拆出残缺的前提。

## 合取分解策略
将目标性质分解为**若干个子模块中的若干条子性质**：children 可以分布
在多个不同子模块中，且【允许一个子模块中拆分出多条子性质】。每个
child 是一个独立的性质（在单一模块内可表达、可独立验证），它们全部
成立即蕴含目标性质。

## 假设引入策略
性质在当前模块内成立，但依赖对输入行为的约束。输出 assumes，
每条 assume 的【后件/单信号】须为目标模块的【输入侧】信号；蕴含前件(停滞条件, 如 (G !p))允许引用任意信号——停滞公平式 (G !目标输出) -> FG 环境输入 的前件引用输出是本质。
注意，当前子模块中之前验证通过的假设均可以利用（kb 中的定理
同样可复用）；对证明性质有帮助的直接引用其公式与信号，不要
重新构造等价的假设。

**禁止 assume 套 assume**：assume 是对当前模块输入行为的约束，
不可能通过在当前模块再添加新的约束来证明（当前模块管不了自己的
输入）。因此兑现节点（locked）只允许合取分解。

**assume 的兑现与跨模块分解**：当一条 assume 在当前模块和候选
模块都无法直接证明时（多落点尝试也失败），说明它需要进一步
分解。此时你可以：
- 将该 assume 改释为**其它模块（通常是信号的驱动模块）上的
  子性质**进行分解——这相当于对该假设做了一次合取分解，
  只是把分解的落点选在了正确的模块上。
- 在 rationale 中说明"该假设需要在模块 X 中分解证明"，输出的
  children 放到模块 X 上。


## 推理方向
采用"从目标反推环境条件"的思路：待证明的性质成立时，需要【其它子模块
满足什么条件】？这些条件又如何从待满足性质的前提推导出来？逐层反推，
直到条件落在某个子模块自身可证的事实上。

## 通路引导(path_guidance)——义务定位提示（建议性, 可不采纳但需给理由）
user 消息中若出现「通路引导(path_guidance)」字段，它是从设计的
通道依赖图静态分析出的义务归属判定与通路族提示：

- verdicts 里每个信号对有一个判定：
  - local: 义务在本模块, 优先单性质模块证明, 不必为它拆分或加 assume；
  - trivial: 模块内无此依赖(前件碰不到后件), 性质自然满足, 不用处理；
  - transfer: 义务在另一个子模块, 可考虑把性质在其端口上重述分解；
  - global: 需要环境组合保证 —— 结合 assumption_hints 生成 assume；
  - env: 纯环境契约(信号由顶层输入驱动或模块观测不到), 作为 assume。
- signal_map 给出公式中每个别名对应的实际信号端口路径。
- families 是通路经语义归类后的族(LLM 归类器的完整输出: name/
  obligation/note/path_count/member_ids): note 是该族通路的语义
  解释(协议行为/义务归属/可疑伪环), member_ids 是属于该族的通路
  序号(完整通路原文见运行目录 drafts 审计文件)。同族通路语义等价,
  按一个骨架处理, 不要逐条生成性质; note 里的义务归属解释
  (环境/设计/可疑伪环)是分解和挂 assume 位置的重要参考。
- 回滚提醒(rollback_notice): 出现即表示上一轮分解方案因验证代价耗尽被
  整体回滚——某个子性质/assume 可能过强(注意: 该性质本身可能正确,
  只是难以兑现)。必须换分解方案或前提形态(更弱/回避式/新增环境
  assume), 不要重复同形式。
选择 assume 的信号时参考 verdict: env 判定(顶层环境驱动)的信号
作 assume 兑现便宜; transfer/global 判定(内部模块驱动)的信号作
assume 时要考虑兑现难度——它可能需要作为驱动模块的设计性质去证明,
裸 assume 不降复杂性。
这些提示是建议性的：以你的推理为准。但当 通路引导 字段存在时,
请在输出 JSON 中附字段 guidance_use 说明利用情况(每轮都要):
{"followed": ["本次性质分解/添加 assume 依赖了的族名或 verdict"],
 "rejected": [{"item": "族名/verdict", "reason": "未依赖的原因,
   如: 该族为伪环不构成义务/已有更强的 KB 定理覆盖/与本轮目标无关"}]}
即: 依赖了哪些要列出; 一个都没依赖也要在 rejected 里说明原因。
该字段不作为拒绝条件, 供运行统计与改进引导质量。

上下文的 RTL 可能是【压缩摘要】(目标性质相关, 名字经过程序校验):
端口表/状态机(枚举准确拼写)/关键寄存器/协议要点。引用信号和状态名
时以摘要为准; 若摘要未覆盖你需要的细节, 用保守的 io.* 端口表达式,
不要猜测内部信号名。

## 可用的推理技巧（最重要——必须对照使用）
（下列公式均为【断言形式】——即输出到 formula 字段的原样文本；
其对应的性质语义由 验证工具 全局检查自动提供，如断言
"(G !p) -> F q" 的性质即 G((G !p) -> F q)。输出时写断言形式、
不要自行添加外层 G。）

**使用义务**：每次决策前必须逐条对照下列技巧自检——rationale 中
须显式写明：目标属于哪类场景（活性/停滞/传播）、哪个技巧适用、
如何套用（套不上也要说明为何不适用）。跳过对照的输出将被拒绝。

**复杂性质必须拆分**：目标或产物中出现下列任一形态时，禁止整条
输出，必须拆成单段性质（每条只含一个蕴含方向/一个因果环节）：
- 多段合取 `(A->B) && (C->D) && (E->F)` → 拆为 A->B、C->D、E->F 各一条
- 长前提链 `A && B && C && D -> E` → 按因果把前提分配到各段
  （如 A&&B -> 中间信号, 中间信号&&C -> D, D&&E' -> 目标）
- 复合结论 `A -> (B && C)` → 拆为 A->B、A->C
拆分的判据：**每条子性质应当能独立通过验证、独立复用**；一条性质
里绑两个以上因果环节 = 后续无法单独兑现/复用, 视为坏输出。

### 技巧一：停滞条件下的公平性假设（假设引入时用）
证明性质 G F p（状态机能一直正常运行，断言写作 F p）时，直接
验证常发现状态机会卡住——因为它在等待其它子模块的响应（对应
其它模块最终被服务，断言 F q）。此时无条件假设 F q 往往过强、
难以表述，可以换用反证式条件假设：
  断言 (G !p) -> F q（性质 G((G !p) -> F q)：若 p 再也不发生，
  则 q 必须最终发生）
它比无条件 F q 更弱（p 正常时对环境零约束），更容易在驱动模块处
兑现；而它被违反意味着环境彻底死停滞，与活性直觉矛盾——因此是
合理的公平性假设形态。

### 技巧二：条件传播链（合取分解时用）
证明断言 (G !p) -> F q（性质 G((G !p) -> F q)）时，可寻找中间
信号 s，按如下推理规则拆分（均为断言形式）：
  (1) (G !p) -> FG s     —— p 长时间不成立，导致关键信号 s
                             最终恒成立（停滞"凝结"为 s）
  (2) (G s)  -> FG q     —— s 恒成立进一步传播，使 q 最终发生
  (3) 断言 (1) ∧ (2) 蕴含 (G !p) -> FG q，更强于目标 (G !p) -> F q
核心：p 的持续失败会凝结到某个信号 s 上，s 又可能继续向外传播。
使用时先总结 p 到 q 的信号通路——通路可能有多条，也可能很长；
每一段传播对应一条子性质（断言），链越长需要拆出的性质越多。

## 性质模式库（最重要——构造公式时尽量从下列模式实例化）

记号说明：`signal1`/`signal2` 等为**任意信号**（端口信号或其布尔组合，
实例化时在 signals 表登记）。每个模板附一个典型使用场景。

**限制自由创造时序结构**：优先从下列模板实例化；如果确需新的时序结构，
必须说明理由——想描述什么时序性质、为什么现有模板无法表达、与哪个
现有模板最接近。

**非必须不新造原子命题（新造变量纪律）**：优先使用现有端口信号的组合
表达；不要随意发明新变量/新谓词（如自造 progress/quiescence 类抽象名）。
若确有必要创造（现有端口确实无法直接表达），必须在 rationale 中说明
必要性——为何现有信号不够、该谓词对应 RTL 什么真实结构。
教训：自造谓词 + 复合前件容易产生"前提直接蕴含结论"的零贡献假设
（实例：前件 G(!(!v||r)) 与结论 F(G v)），白白消耗分解配额。

### 安全层（组合不变量）
- 模板: `!(signal1 & signal2)` / `(!signal1 | signal2)` / `!signal1`
  描述: 组合不变量——任意信号的布尔组合, 上述三种是简单形式, 实际种类很多。
  对应场景: `!(signal1 & signal2)` 表示信号间互斥, 如仲裁器两条请求线
  不同时有效（读写互斥）; `(!signal1 | signal2)` 等价于`(signal1 -> signal2)`,
  表示信号间的蕴涵关系, 如 dcache 侧写握手完成则必然传播为对外写握手完成
  （`!dcacheWriteReqFire | nastiWriteReqFire`）; `!signal1` 表示信号恒低,
  如配置输入永久关闭 !abort。

### 活性层（一般性从高到低）
- 模板: `signal1 -> F signal2`
  描述: 基本响应公平——signal1 成立后 signal2 最终出现。
  对应场景: 请求线拉起后授权最终到来。完整实例:
  `nastiReadReqValid -> F nastiReadReqReady`（读请求有效后, 总线读授权
  最终到来）。最常用的公平假设形状。
  与其它模板关系（模板替换）: 模块级不可证时, 可以考虑降级为
  `(G signal1) -> F signal2`，后者对前提条件要求更严格，更容易满足。

- 模板: `(G signal1) -> FG signal2`
  描述: 静默传导——signal1 长期发生时, 效果"凝结"到 signal2 上使其最终
  恒成立。
  对应场景: 最典型的**最终目标形式**（冻结性质）。完整实例:
  `(G !cpuReqValid) -> FG !nastiReadReqValid`（cpu 请求永久停止后,
  总线读请求最终永久消失）。
  与其它模板关系（模板替换）: 模块级不可证时, 可以考虑降级为
  `(G signal1) -> F signal2`，后者对结论要求更宽松，更容易满足。

- 模板: `(G signal1) -> F signal2`
  描述: 停滞前件公平——signal1 **持续**成立时 signal2
  最终出现。
  对应场景: 请求恒存的停滞场景下授权最终到来; 持续前件让仲裁类模块可
  直接证。完整实例: `(G nastiReadReqValid) -> F nastiReadReqReady`
  （读请求持续有效时, 授权最终到来）。

- 模板: `signal1 -> (signal1 U signal2)`
  描述: 稳定性——signal1 保持到 signal2 出现。
  对应场景: master 请求纪律。完整实例: `nastiReadReqValid ->
  (nastiReadReqValid U nastiReadReqFire)`（读请求保持到握手完成）。
  与其它模板关系（模板替换）: **慎用**——强 U 自带 eventuality, 本模板
  蕴含 `signal1 -> F signal2`, 因此也可以考虑降级为
  `(G signal1) -> F signal2`。

- 模板: `signal1 -> X F signal2`
  描述: 响应到达——事件发生后（下一拍起）结果最终到来。
  对应场景: 握手 fire 后数据/响应 valid 最终出现。完整实例:
  `nastiReadReqFire -> X F nastiReadRespValid`（读地址握手后, 响应
  最终出现）。及时性基础层, 不约束具体拍位。
  与其它模板关系（模板替换）: 该模板实际上蕴含`signal1 -> F signal2`，严格要求
  `signal2`的出现比`signal1`晚，可以描述比`signal1 -> F signal2`更精确的时序关系

- 模板: `signal1 -> X (signal2 U signal3)`
  描述: 持续参与——事件发生后保持消费直到完成。
  对应场景: 写事务发起后 w.ready 保持到 last 拍。完整实例:
  `nastiWriteReqFire -> X (nastiWriteMemReady U (nastiWriteMemReady
  & nastiWriteRespFinsh))`（写地址握手后, 写数据通路保持就绪直至末拍）。

- 模板: `F (!signal1 || signal2)`
  描述: 弱公平（条件公平）——signal1 消失或 signal2 到来, 至少其一
  最终发生。
  对应场景: 读请求最终消失或被授权——请求撤回同样兑现。完整实例: `F (!nastiReadReqValid
  || nastiReadReqReady)`。
  与其它模板关系（模板替换）: 比 `signal1 -> F signal2` 弱（允许撤回
  兑现）。

- 模板: `signal1 -> X F (signal2 ##N signal3)`
  描述: 成对窗口——事件后间隔 N 拍先后完成（signal2/signal3 为拍事件
  原子, N 常取 1 表示相邻两拍）。
  对应场景: 读响应"非last拍紧跟last拍"的成对握手。完整实例:
  `nastiReadReqFire -> X F ((nastiReadRespFire & !nastiReadRespFinsh) ##1
  (nastiReadRespFire & nastiReadRespFinsh))`。
  

- 模板: `signal1 -> (!signal2 ##N (signal1 & signal2))`
  描述: 帧形状——数据拍存在时锚定末拍（signal2 为末拍标记, N 常取 1）。
  对应场景: 总线响应帧的拍位约定。完整实例: `nastiReadRespValid ->
  (!nastiReadRespFinsh ##1 (nastiReadRespValid & nastiReadRespFinsh))`。

- 模板: `F (布尔式)`
  描述: 一般公平性——F 可包裹任意布尔表达式（信号、`a & b`、`a -> b`、
  `G p` 等）, 语义"最终该式在某拍成立"。
  对应场景: 无前件的基础公平, 完整实例 `F nastiReadReqReady`（外部读
  授权最终出现）; 终局恒真形式 `F (G signal1)`, 实例 `F (G !dcacheWriteReqValid)`。

### 性质模式与条件传播链关系
做性质分解时, 条件传播链（技巧二）给出**拆分骨架**, 模式库提供**每一段
的填写形状**:
- 基本思想: 使用条件传播链时, 结合数据通路分析信号间的依赖关系, 将
  `(G signal1) -> F signal2` 或 `(G signal1) -> FG signal2` 类性质分解。
- 链头/链中: 通常采用 `(G signal1) -> FG signal3`（signal 取反式即可
  表达"不发生"）。signal3 是 signal1 到 signal2 数据通路上的**中间信号**
  ——它受到 signal1 的影响, 又进一步影响 signal2。如此逐段接续, 即可
  将传播链持续延长。
- 链尾: 按目标性质的结论选择形状——目标是终局恒真用
  `(G signalN) -> FG signal2`, 只需一次发生用 `(G signalN) -> F signal2`。
- 每一段传播不可直接断言时, 为该段选择支撑模板（添加 assume）;
  多条通路 = 多条链分别拆分, 每段一条子性质。
- 链上模板混用是常态（断言段 + 假设段交替）。

## 时序公式语法铁律（违反直接编译失败）
CHA 的 LTL 文法分两层, 规则不同, 混用是编译失败的头号原因:
1. **## 只能出现在序列层**: `A ##N B` 中 A、B 各自必须是
   单信号 / !单信号 / 括号子序列。## 不能出现在 U、F、G、&&、||
   的裸操作数位置。
2. **序列层布尔用单字符 & 和 |**: 双字符 && / || 只属于性质层
   (G/F/X/U/-> 所在层)。在 ## 两端的括号里写 && 会直接解析失败。
3. **蕴含前件是序列**: `seq |-> prop` / `seq |=> prop` 的左边享受
   完整序列语法(可含 ##、[*m] 重复), 右边是普通性质。
合法示例:
  (V & !L) ##1 (V & L)            成帧: 非末拍后一拍到末拍
  req |-> F resp                  窗口蕴含
  cpuReqValid -> X (V U (V & L))  混合: 性质层 X/U, 序列层 &
非法示例:
  F ((V && !L) ##1 (V && L))      ✗ 序列层用了 &&(应为 &)
  X ((!V U (V && !L)) ##1 ...)    ✗ ## 挂在性质层算子旁
  A ##1 (B || C)                  ✗ 序列层用了 ||(应为 |)
先验 X3/X4 与 kb 中已证式即按此语法书写, 可直接作模板。

## 信号可以用 Chisel 表达式
signals 条目除纯路径 port 外，可用 expr 给出 Chisel 表达式（等号右边
原样编译），例如握手信号：
  "reqFire": {"module": "ICache", "expr": "io.nasti.ar.fire"}
表达式中的信号必须存在于该模块；多位向量当布尔用时需自行保证
类型正确。


   round_history 字段记录本目标此前各轮的分解结果（哪些子性质
   已证/失败/跳过）。利用这些信息：已证的直接引用（在 kb 中），
   失败的避免重复同样思路，据此调整下一轮分解策略。

   lineage 字段给出当前性质的来源谱系：parent（产生它的分解决策与
   策略）、siblings（同轮其它子性质/假设的结果与状态）、
   origin_assume（若本性质是某假设的兑现）。利用这些信息：
   兄弟中已通过的性质说明方向正确可直接借鉴/复用；已失败的避免
   重复同样思路；结合本性质自身的失败史调整分解。

   known_signals 字段列出当前已声明的信号（alias/module/path）。
   **必须优先复用其中与目标线一致的信号**——引用同一根线时直接
   使用已有 alias，不要另起新名（例如清单里已有
   nastiReadReqReady=ICache.io.nasti.ar.ready 时，你的 signals 应
   沿用该别名而非再造 arReady/readReqReady）。只有清单中不存在
   对应信号时才声明新条目。

# 硬性规则（违反即被拒绝）
1. 一次只选一种策略；合取分解时 children 非空且 assumes 不出现，
   假设引入时 assumes 非空且 children 不出现。
2. formula 使用类 SVA 的 LTL 语法（G/F/X/U、!、&&、||、->、##1），
   原子命题只能是 signals 表中出现的【单个信号名】，禁止路径前缀。
   【断言的两种语义（assert_kind 字段必须显式给出）】
   - "global"（默认）：全局断言——chaAssert 在每个周期检查，
     断言 p 的语义就是 G p。给出最简公式即可，不要额外加外层 G。
   - "once"：一次性断言——仅描述从初始时刻起的行为（如复位后
     必达某状态），公式需自含初始语义。
   每条 child/assume 都要带 "assert_kind": "global" 或 "once"。

3. signals 映射：公式中的每个裸信号名都必须有对应条目
   {"模块": {"module": ..., "port": <该模块端口下的信号路径>}}。
4. 分属多个模块的信号且声明 atomic 时必须给出 "module" 字段指明归属。
5. assume 信号分域: 蕴含式的后件/单信号性质(如 F x)须在目标模块
   输入侧(Input); 蕴含前件及其它形态(U/合取等)允许任意方向。
   约束模块自身输出行为的仍应改释为子性质, 不是 assume。
6. 若 constraints.locked 为 true（兑现节点），只允许合取分解。
7. **渐进式知识积累**：验证是逐条进行的——全局 BMC 筛选通过的性质
   会进入模块级完备证明（BMC→IC3），完备证毕者入 KB 并永久保留，
   即使本轮整体有效性不足已证的也不丢弃。
   每轮分解时：
   - 优先引用 kb_available 中已证性质（它们是可靠的知识）
   - 不必一次性生成完整的蕴含集——提供部分有意义的性质即可，
     框架会保留已证部分，下一轮在此基础上补充
   - 避免与 neg_kb 中已证伪结论重复；priors 已自动注入验证
8. **推荐将目标性质分解为其它若干子模块中的若干条子性质**（数量不限，按需拆分；至少 2 条）：
   允许跨多个子模块分布，也允许同一子模块中拆出多条——每条子性质
   会被分别加入任务队列独立验证，小而具体的性质比大而全的更容易
   证明。各 child 的 signals.module 填各自宿主模块，端口必须真实
   存在。assume 同理可多条（数量不限）。
   **按置信度排序输出**：你认为最可能正确的子性质/假设放在数组
   最前面（验证按顺序进行，靠前者优先被检查与验证）。
9. rationale 必须说明为什么该策略可行；若不采纳 history 中的 hint，
   必须解释原因。

# 输出格式（只输出 JSON，无其它文本）
{"strategy": "CONJUNCT" | "ASSUME",
 "rationale": "...",
 "children": [{"id": "P1.1", "nl": "...", "formula": "...",
               "assert_kind": "global" | "once",
               "signals": {"信号名": {"module": "...", "port": "..."}},
               "module": "归属模块(仅 atomic 多模块时)"}],
 "assumes":  [{"id": "A1", "nl": "...", "formula": "...",
               "assert_kind": "global" | "once",
               "signals": {...}, "target_module": "..."}]}
（未使用的数组输出为空数组 []）
""")


class DecomposeError(Exception):
    pass


def _check_signals(sig: Dict, where: str):
    if not isinstance(sig, dict) or not sig:
        raise DecomposeError(f"{where}: signals 必须是非空对象")
    for name, s in sig.items():
        if not isinstance(s, dict) or "module" not in s:
            raise DecomposeError(
                f"{where}: 信号 {name} 缺 module 字段")
        if not (s.get("port") or s.get("expr")):
            raise DecomposeError(
                f"{where}: 信号 {name} 需 port(纯路径)或 expr(Chisel表达式) 之一")


def strip_outer_g(formula: str) -> str:
    """global 断言摄入规范化: 最外层是 G 应用时剥掉（断言语义即 G）。
    仅当括号配平确认整体是 G(...) 或 'G <原子式>' 时剥; 否则原样。"""
    s = formula.strip()
    if s.startswith("G") and len(s) > 1 and s[1] not in "()!A-Za-z0-9_".replace("()", ""):
        pass
    # 形态1: G(....) 且括号配平
    if re.match(r"^G\s*\(", s):
        depth, i = 0, s.index("(")
        for j in range(i, len(s)):
            if s[j] == "(":
                depth += 1
            elif s[j] == ")":
                depth -= 1
                if depth == 0:
                    inner = s[i + 1:j].strip()
                    if j == len(s) - 1 and inner:      # 最外层闭合即结束
                        return inner
                    break                                # 后面还有内容 → 不是整体 G 应用
    # 形态2: G <裸式> (如 "G F response")
    m = re.match(r"^G\s+([FA-Za-z_][\w\s()!&|><=#\-]*?)\s*$", s)
    if m and "->" not in s[:2]:
        return s[1:].strip()
    return s


def _normalize_kind(item: Dict) -> Dict:
    """断言语义归一: 校验 assert_kind + global 剥外层 G"""
    kind = item.get("assert_kind", "global")
    if kind not in ("global", "once"):
        raise DecomposeError(
            f"assert_kind 须为 global/once, 得到 {kind}")
    item = dict(item)
    item["assert_kind"] = kind
    if kind == "global":
        item["formula"] = strip_outer_g(item["formula"])
    return item


def _formula_atoms_ok(formula: str, sig: Dict, where: str):
    """公式中的标识符必须是 signals 键（保守: 抽取裸标识符比对）"""
    atoms = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", formula))
    keywords = {"G", "F", "X", "U"}
    unknown = {a for a in atoms - keywords - set(sig)
               if len(a) > 1}        # 忽略单字母变量误报? 不, 一并检查
    unknown = {a for a in atoms - keywords - set(sig)}
    if unknown:
        raise DecomposeError(
            f"{where}: 公式引用了未在 signals 声明的信号 {sorted(unknown)}")


_TAUT_PATTERNS = [
    r"G?\(?\s*(\w+)\s*->\s*\1\s*\)?",       # A -> A / G(A -> A)
    r"G?\(?\s*(\w+)\s*\|\|\s*!\1\s*\)?",  # A || !A
]


def _degenerate(formula: str, parent_formula: str = None,
                seen: Optional[set] = None) -> Optional[str]:
    """返回退化原因; 非退化返回 None。只查常见模式, 保守。"""
    if not ANTI_DEGENERATE:
        return None
    norm = re.sub(r"\s+", "", formula)
    if parent_formula and norm == re.sub(r"\s+", "", parent_formula):
        return f"公式与父节点完全相同（原地打转）"
    for pat in _TAUT_PATTERNS:
        if re.fullmatch(pat, norm):
            return f"公式 '{formula}' 是永真式"
    if seen is not None and norm in seen:
        return f"公式 '{formula}' 与另一 child 重复"
    return None


def validate_decision(dec: Dict, locked: bool = False,
                      parent_formula: str = None,
                      candidate_ids: List[str] = None) -> Dict:
    """schema 校验。通过返回规范化决策, 失败抛 DecomposeError。
    candidate_ids 非空时(BFS 候选池模式): 每个候选必须表态——
    (候选池机制已移除, 2026-10-08; 保留参数兼容旧调用, 恒为 None)。"""
    if not isinstance(dec, dict):
        raise DecomposeError("决策不是 JSON 对象")
    strategy = dec.get("strategy")
    if strategy not in ("CONJUNCT", "ASSUME"):
        raise DecomposeError(f"strategy 必须是 CONJUNCT/ASSUME, 得到 {strategy}")
    if not dec.get("rationale"):
        raise DecomposeError("缺少 rationale")

    out = {"strategy": strategy, "rationale": dec["rationale"]}
    if dec.get("guidance_use"):
        out["guidance_use"] = dec["guidance_use"]

    # 候选池表态校验已移除 (2026-10-08 用户裁定取消候选池机制):
    # 输出中的 used/dropped_candidates 字段被静默忽略, 不再强制表态
    for k in ("used_candidates", "dropped_candidates"):
        dec.pop(k, None)

    if strategy == "CONJUNCT":
        children = dec.get("children") or []
        if dec.get("assumes"):
            raise DecomposeError("禁止混合: CONJUNCT 不允许 assumes")
        if len(children) < 2:
            raise DecomposeError(
                f"children 至少 2 条(1 条无分解意义), 得到 {len(children)}")
        norm = []
        seen_formulas = set()
        for c in children:
            if not c.get("formula"):
                raise DecomposeError("child 缺 formula")
            c = _normalize_kind(c)
            _check_signals(c.get("signals"), f"child {c.get('id')}")
            _formula_atoms_ok(c["formula"], c["signals"],
                              f"child {c.get('id')}")
            reason = _degenerate(c["formula"],
                                 strip_outer_g(parent_formula) if parent_formula else None,
                                 seen_formulas)
            if reason:
                raise DecomposeError(f"child {c.get('id')}: 退化分解——{reason}")
            seen_formulas.add(re.sub(r"\s+", "", c["formula"]))
            norm.append({"id": c.get("id"), "nl": c.get("nl", ""),
                         "formula": c["formula"], "signals": c["signals"],
                         "assert_kind": c["assert_kind"],
                         **({"module": c["module"]}
                            if c.get("module") else {})})
        out["children"] = norm
    else:
        assumes = dec.get("assumes") or []
        if dec.get("children"):
            raise DecomposeError("禁止混合: ASSUME 不允许 children")
        if locked:
            raise DecomposeError("兑现节点(locked)只允许 CONJUNCT")
        if not (1 <= len(assumes) <= 3):
            raise DecomposeError(f"assumes 数量须 1~3, 得到 {len(assumes)}")
        norm = []
        for a in assumes:
            if not a.get("formula"):
                raise DecomposeError("assume 缺 formula")
            if not a.get("target_module"):
                raise DecomposeError("assume 缺 target_module")
            a = _normalize_kind(a)
            _check_signals(a.get("signals"), f"assume {a.get('id')}")
            _formula_atoms_ok(a["formula"], a["signals"],
                              f"assume {a.get('id')}")
            norm.append({"id": a.get("id"), "nl": a.get("nl", ""),
                         "formula": a["formula"], "signals": a["signals"],
                         "assert_kind": a["assert_kind"],
                         "target_module": a["target_module"]})
        out["assumes"] = norm
    return out


def decompose(context: Dict) -> Dict:
    """调 LLM 做分解决策。context 见模块 docstring。
    校验失败自动回炉（把错误信息作为反馈再问, 最多 MAX_REPAIR_ROUNDS 次）。
    """
    locked = bool(context.get("constraints", {}).get("locked"))
    history = []
    for i in range(MAX_REPAIR_ROUNDS + 1):
        payload = dict(context)
        if i > 0:
            payload["repair_feedback"] = history
        r = chat("decomposer", DECOMPOSER_PROMPT, payload)
        dec = r["parsed"]
        if dec is None:
            history.append("上一轮输出不是合法 JSON, 请重新输出纯 JSON 对象")
            continue
        try:
            _node = context.get("待验证性质(当前分解目标, node)") \
                or context.get("node") or {}
            parent_formula = _node.get("formula")
            return validate_decision(dec, locked, parent_formula, None)
        except DecomposeError as e:
            history.append(f"上一轮决策被拒绝: {e}")
    err = DecomposeError(
        f"decomposer 连续 {MAX_REPAIR_ROUNDS + 1} 轮输出不合格: "
        f"{history[-1] if history else '未知'}; 修复史: "
        + " | ".join(history[-3:]))
    err.raw_head = str(r.get("content", ""))[:160]
    raise err
