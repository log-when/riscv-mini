# AGVerify：Agent 驱动的 Assume-Guarantee 组合形式化验证框架

设计基准文档。所有实现以此为准，修改需先改本文档。

## 0. 概述

对 Chisel 设计（riscv-mini）做 agent 驱动的假设-保证（assume-guarantee）
组合验证。Agent 扮演"组合推理者"，CHA 模型检测器扮演"定理检查器"
（直接消费 Chisel，支持 BMC / IC3 / 蕴含检查）。

核心循环：agent 将待证性质分解（合取分解 or 引入 assume），脚本用
全局 BMC 廉价筛选分解结果，通过者进入模块级 IC3 完备证明；失败则
归因反馈、局部/全局回溯，直到证明树全部证毕。

```
              ┌────────────────────────────────────────┐
              │              证明树生长循环              │
              │                                        │
  输入性质 ──▶│ decomposer ──▶ dispatcher(BMC) ──▶ validator(IC3)
  (1 条)      │    (LLM)          (脚本)              (脚本+CHA)
              │      ▲               │ FAIL              │
              │      │               ▼                   │
              │      └──────── critic (LLM, CEX 摘要)     │
              │                  局部/全局回溯             │
              └────────────────────────────────────────┘
```

## 0.5 递归证明结构

整个框架是同一个证明原语在不同层级的自相似应用：

```
目标 G 在模块 M 中证明
  = 找一组条件 C（children 的 guarantees 或 assumes）
    使 C ∧ M → G          ← 所有层级共用同一证明形状
    且 C 中每条兑现时又成为新目标，递归下降
```

- CONJUNCT 路：C = 子性质合取，递归发生在子节点
- ASSUME 路：本层证 `A ∧ M → P`；递归发生在 A 改释为 assert 的
  兑现节点
- 递归终点：某个目标能被 IC3 直接证掉（无新条件），即叶子

主循环本质上是**由 agent 搜索分解策略、由 CHA 逐节点盖章的递归证明
搜索**；agent 的唯一职责是在每层选出"最可能被 CHA 证掉"的 C。

终止性由三条结构性约束保证：

1. 兑现节点只准走 CONJUNCT（禁止 assume 链）→ 递归不绕环
2. 树有限、回溯有熔断（总轮数上限）
3. 每层兑现检查 `Global → A` 使 proof obligation 单调递减，
   无自我指涉

## 1. 输入格式

### 1.1 hierarchy.json（模块拆分 + 工作文件）

- 由使用者一次性封装提供；验证运行中 agent 的读写均在此文件或其拷贝上进行
- 连接只到**模块 + 端口组**粒度；端口内信号级匹配由 agent 按需调
  `read_design` 核对
- 所有连接默认同层父子关系（无 via 概念）

```json
{
  "modules": [
    {"name": "Tile",     "src": "src/main/scala/mini/Tile.scala"},
    {"name": "Datapath", "inst": "core",   "parent": "Tile", "src": "..."},
    {"name": "ICache",   "inst": "icache", "parent": "Tile", "src": "..."},
    {"name": "DCache",   "inst": "dcache", "parent": "Tile", "src": "..."}
  ],
  "connections": [
    {"from": "Datapath.imem", "to": "ICache.io"},
    {"from": "Datapath.dmem", "to": "DCache.io"}
  ]
}
```

### 1.2 properties.json（待证性质，一次一条）

```json
{
  "id": "P1",
  "scope": "atomic",
  "module": "ICache",
  "nl": "CPU 发出取指请求后，ICache 必须最终返回有效数据",
  "formula": "G(req -> F resp_valid)",
  "signals": {
    "req":        {"module": "ICache", "port": "io.cpu.req.valid"},
    "resp_valid": {"module": "ICache", "port": "io.cpu.resp.valid"}
  }
}
```

约定：

- **formula**：类 SVA 的 CHA 格式；原子命题只能是**单个信号名**（裸名，
  无路径前缀），跨模块消歧完全依赖 signals 映射表
- **nl**：自然语言语义，供 decomposer 理解
- **scope**：提供方声明（atomic / composite）；**声明 atomic 且信号
  分属多模块时必须同时指明 module 字段**（归属子模块，由脚本校验）
- **signals**：公式裸信号名 → 模块 + 信号路径的映射

对性质提供方的要求：**所有 signals 必须能归属到唯一的同一模块**
（信号分属不同模块但经连接共同落在同一父模块边界上时，以父模块为
归属）。无法满足时性质必须先人工改写或预分解。

### 1.3 设计源码

Chisel 源码只读。不预建索引（避免与源码不同步），通过 `read_design`
工具按需查询模块端口、信号类型、子模块实例。

## 2. 性质分类：classify_prop（纯脚本）

在性质读入时、以及**每个新节点入树时**运行（证明树不变式：树中节点
必带合法 derived 字段）。

```
输入: property.signals, hierarchy.json
1. |S| == 1 → atomic，归属该模块（若声明了归属且与之矛盾 → 拒绝）
2. |S| > 1  → 信号合一：连接两侧端口字段指同一物理连线
   （Datapath.imem.req.valid ≡ ICache.io.req.valid）
   - 声明 atomic 时：**必须指明归属 module 字段**，脚本校验所有
     信号都能以该模块视角表达（宿主或经直接连接的同一连线），
     校验失败 → 一致性门拒绝；通过 → atomic，signals 重映射为该
     模块视角（端口组前缀替换、字段后缀保留、via 记录原始引用）
   - 未声明 atomic：自动合一，存在唯一可表达模块则 atomic（提示
     声明保守），否则 composite
```

**归属由提供方声明、脚本校验**——避免自动选择策略选到过大验证对象
（模块级 IC3 的状态空间差异可达数量级）。decomposer 产出的 atomic
children 同样必须带 module 字段。

注意：**"存在共同父模块但信号不落在同一子模块"不构成 atomic**——
验证在子模块内进行（模块级 IC3），父级共同可观察不足以支持。

已知限制（v1 接受的假定）：
- **字段后缀移植不校验**：重映射把信号的字段后缀原样移植到对端
  端口前缀下，不验证对端是否真有该字段。`<>` 整体连接时 Chisel
  类型系统保证两侧结构一致，假定天然成立；`:=` 单向连接时对端可能
  缺字段——**校验交由 CHA 在验证时做**（或验证前的编译检查）：
  错误路径会作为未知信号被 CHA 报错，dispatcher 将其归因反馈回
  decomposer，不做独立的字段比对
- **隔层/透传合一不做**：信号宿主与候选模块之间只查一跳直接连接；
  模块内部端口透传关系不在 hierarchy.json 中，无法表达

派生字段（脚本生成，agent 只读）：

```json
"derived": {
  "scope": "atomic",
  "module": "Tile",
  "signals": {"...": "重映射后的父模块视角端口路径"}
}
```

- **scope 一致性校验**（提供方质量门）：
  - 声明 atomic / 计算 atomic → 通过
  - 声明 composite / 计算 composite → 通过（derived 无 module/signals）
  - 声明 atomic / 计算 composite → **读入时拒绝**，报告原因
  - 声明 composite / 计算 atomic → 通过，按 atomic 处理，日志提示

## 3. 全局数据结构（三件套）

### 3.1 proof_tree（证明树）

```json
{
  "root": "P1",
  "nodes": {
    "P1":   {"strategy": "CONJUNCT", "children": ["P1.1", "P1.2"],
             "status": "BMC_FILTERED", "fail_count": 0},
    "P1.1": {"strategy": "ASSUME", "assumes": ["A1"],
             "status": "PENDING", "fail_count": 2},
    "A1":   {"kind": "assume", "discharged_by": "P1.3",
             "status": "IC3_PROVEN"}
  },
  "pending_queue": ["P1.1"],
  "round": 7
}
```

节点状态机：

```
PENDING → BMC_FILTERED → IC3_PROVEN    (终态，仅叶子)
PENDING → BMC_FAILED / IC3_FAILED / TIMEOUT_UNPROVED
```

**节点 PROVEN 语义（自底向上）**：

- 叶子：IC3 证明 `A ⊢ Mᵢ |= φ`
- 中间节点，两条路径任一即可：
  - 路径 A（纯合取）：`∧(已证 children) ⊢ parent`，将蕴含编译为
    CHA 性质 `G(antecedent -> consequent)` 跑完备检查
  - 路径 B（assume-guarantee）：已有性质蕴含出该节点所需 assumes
    （`assume_sources` 指向树上已 PROVEN 节点，蕴含关系同样自动挂树
    为兑现节点），且在 assumes 约束下 parent 成立

**assume 的兑现规则**：节点走 ASSUME 路线产生的每条 assume 自动成为
新的验证目标节点挂树，其证明**只允许走 CONJUNCT 路线**（禁止 assume
套 assume，杜绝循环假设）；当该 CONJUNCT 节点的全部子节点验证完成
（蕴含检查通过）后，assume 才算 discharged，原节点的证明前提才成立。

**结局标签与 BMC 的隐含关系**（实现约定）：非 VIOLATED 的结局
（PROVEN / TIMEOUT / ITER_EXCEED）一律隐含"BMC 筛选已通过"——BMC
是前置关卡，不存在"BMC 通过与否未知"的终态。失败账本中 TIMEOUT 条目
因此携带确定信息："BMC k 步内成立 + 假设有效，但完备证明未收敛"。

**KB（定理库）复用规则**：
- **状态机含 MOD_PROVEN**（模块级条件已证）：`A ⊢ M |= P` 的 IC3
  通过后先标 MOD_PROVEN，**不进 KB**；P 的全部 assume 兑现完成后才
  升级 IC3_PROVEN 并写 KB——**KB 恒为无条件定理，无需作废级联**
- 仅 IC3_PROVEN 的 assert/assume 进 KB；BMC 通过**不进**（有界事实
  非定理）
- 签名匹配**不限模块**（wire 是全局物理对象，公式含义由 wire 集合
  完全决定）
- **双重复用机制**：机械层（任务开场签名查 KB，命中直接 PROVEN）+
  提示层（decomposer 上下文附带 KB 摘要——供其分解时主动靠拢已有
  结论；critic 反馈亦可引用）
- **反 KB（负面知识）**：VIOLATED 结论按签名索引，跨子任务可见；
  任务开场正负双查——反 KB 命中则直接失败短路（同签名全局 BMC 结论
  确定，重跑必败）；TIMEOUT 仅提示性。兄弟负短路：unwind 时检查
  兄弟任务是否已在反 KB，命中即标记失败跳过
- 失败账本 failures 带 outcome（VIOLATED / TIMEOUT / ITER_EXCEED），
  assert 与 assume 一视同仁；兑现是递归深度优先子任务（任务栈），
  失败作废动作嵌在弹栈处、回滚由 unwind 完成

**循环依赖防护**（assume 语义环，如 A1 兑现中又提出等价 assume）：
1. 签名级（主力）：add_assume 时与【栈上祖先未清偿 assume 签名集】
   比对，命中拒绝该分解决策
2. discharge 链深度预算（MAX_DISCHARGE_DEPTH，默认 3）：兜住换写法
   的语义等价环
3. 全局轮数熔断：最终保险

**assume 公式的双重身份**（严格区分，不得混淆）：

- **身份 1（作为 assume，用于证明 P）**：写入目标模块性质文件，仅作
  Mᵢ 的 IC3 证明前提（`A ⊢ Mᵢ |= P`），A 本身不需要证明，只需全局
  矛盾检查通过
- **身份 2（作为验证目标，兑现 A）**：兑现时 A **改释为 assert**，在
  能观察到其信号被实际驱动的层级（writer 所在环境，通常为父模块/
  全局）作为 assert 验证，走 CONJUNCT 分解
- assume **不会也不应在目标模块内部被证明**——它约束的是输入侧行为，
  子模块无法保证自己的输入。若某 assume 在 Mᵢ 内部即可作为 assert
  证明，说明 assume 书写错误（约束了模块自身行为而非环境输入）。
  由此增加一条 validator 校验：**assume 引用的信号必须全部位于目标
  模块的输入侧**（端口方向为 Input），否则拒绝该 assume

### 3.2 signal_registry（信号登记表）

每个物理信号一个 canonical ID，所有性质中的信号引用归一到 ID 上：

```json
{
  "Tile.icache.io.cpu.req.valid": {
    "declared": {"module": "ICache", "inst": "icache",
                 "path": "io.cpu.req.valid", "type": "Bool"},
    "referenced_by": [
      {"node": "P1",   "local_name": "req"},
      {"node": "A1",   "local_name": "cpu_req"}
    ],
    "writer": "Datapath", "readers": ["ICache"]
  }
}
```

- **canonical ID**：`{父模块路径}.{实例名}.{信号路径}`；同一物理信号
  的子模块视角与父模块边界视角（classify_prop 重映射产物）归为同一 ID
- **由脚本维护**（节点入树时注册，回滚时移除引用），agent 只读
- **驱动关系（writer/readers）**：按模块端口方向（Chisel
  Input/Output）+ 端口级连接展开（含 `<>`/`:=` bundle 展开到字段）
  静态计算一次；不追踪模块内部信号的驱动链

支撑机制：

1. 同信号归一发现：children 与已 PROVEN 节点 canonical ID + formula
   结构一致 → 复用证明，不重复验证（收敛加速器）
2. assume 兑现匹配：assume 约束的信号由 writer 模块的 guarantee 兑现
3. 一致性闸门：local name 一致但 canonical ID 不同 → 拒绝（agent 信号
   错配）；同一 canonical ID 在 children 中被声明为不同模块信号 → 校验失败
4. 无环检查在驱动图上直接可见

### 3.3 current（游标，非关键）

```json
{"node": "P1.2", "phase": "DECOMP", "round": 7}
```

用于断点续跑与日志定位，不参与判定逻辑。

## 4. 角色分工

**两 LLM agent + 两程序模块**。dispatcher/validator 逻辑机械，纯代码
实现；只有 decomposer 和 critic 需要 LLM。

### 4.1 decomposer（LLM）

读：当前 PENDING 节点性质（formula+nl+derived）、相关子模块接口摘要
（read_design 按需）、本节点失败历史（截断）。不读全设计源码。

输出决策 JSON（**单策略，禁止 CONJUNCT/ASSUME 混合**）：

```json
{
  "node": "P1",
  "strategy": "CONJUNCT",
  "rationale": "...（人读的分解依据）",
  "children": [
    {"id": "P1.1", "nl": "...", "formula": "...", "signals": {...}}
  ]
}
```

ASSUME 策略时：

```json
{
  "node": "P1.1",
  "strategy": "ASSUME",
  "rationale": "...",
  "assumes": [
    {"id": "A1", "nl": "...", "formula": "...",
     "signals": {...}, "target_module": "ICache"}
  ]
}
```

- children/assumes 条目即 property/assume 对象，**不带 scope/derived**
  （由 classify_prop 入树时补算）
- 兑现目标节点由 dispatcher 自动挂树，decomposer 不操心

### 4.2 dispatcher（程序）

- 驱动主循环；维护 proof_tree / signal_registry / current
- 全局 BMC 筛选：对 children 在**完整大模块**上 `cha_verify(mode=bmc)`
  （两类策略统一：都做全局 BMC 筛选）
- assume 入树前在 CHA 做**全局矛盾检查**（assume 与真实环境无矛盾，
  比 cover 更强，排除 vacuous）
- 无环检查（依赖边/驱动图遍历）
- 兑现节点自动挂树
- 失败历史维护（failures.jsonl，只追加）

### 4.3 validator（程序）

ASSUME 路线入 IC3 前的门槛（简化后）：

1. 全局矛盾检查（CHA，见 4.2）
2. 无循环依赖（图检查）
3. assume 信号方向检查：assume 引用的信号必须全部位于目标模块的
   输入侧（端口方向为 Input），否则判定 assume 书写错误，拒绝

通过后：assume 写入目标模块性质文件 → `cha_verify(mode=ic3)` 证明
`A ⊢ Mᵢ |= φ`（assume 仅作前提，兑现见 §3.1 双重身份规则）。
中间节点蕴含检查同样编译为 CHA 性质走完备模式。

（悬空 assume 不作为门禁：运行中允许暂时悬空，最终树上必然不悬空
——自动挂树保证"无 PENDING 即无悬空"。）

### 4.4 critic（LLM）

归因基本机械可判，critic 的价值是把 CEX 摘要为 decomposer 可用的
反馈文本：

```
BAD_DECOMP          分解出的性质本身不成立 → 局部回滚重分解
CONTRADICT_ASSUME   全局 BMC 未通过（assume 与真实环境行为不符）
                    → 重新设计 assume（弱化/替换），效果类似回滚
IMPLICATION_GAP     中间节点蕴含检查失败 → 回滚补充分解
REAL_BUG            仅出现在输入性质初检阶段；循环中不产生
                    （完整反例路径论证成本过高）
BOUND_SHORT         占位标记，暂不处理；窗口边缘失败时人工判断是否
                    加深 bound 重跑
```

BAD_DECOMP 与 CONTRADICT_ASSUME 的区分可由节点 strategy 机械判定
（CONJUNCT→前者，ASSUME→后者），无需 LLM 归因。

失败反馈注入格式（下一轮 decomposer 上下文）：

```json
{
  "round": 3, "node": "P1.1",
  "attempt_history": [
    {"round": 1, "strategy": "ASSUME", "outcome": "BMC_FAIL",
     "cause": "CONTRADICT_ASSUME",
     "evidence": "CEX 摘要：t=4 ...",
     "hint": "建议弱化 A1 为 ..."}
  ]
}
```

- hint 是建议非指令；decomposer 不采纳时必须在 rationale 中回应
- 历史只追加；局部回滚保留本节点历史，全局回滚保留整棵失败子树历史

## 5. 验证工具层（CHA）

CHA 直接消费 Chisel，一个统一入口：

| tool | 功能 |
|---|---|
| `cha_verify` | `(chisel路径, 性质集, mode: bmc/ic3, bound?)` → `{verdict: PASS/FAIL/UNKNOWN, cex?}` |
| `parse_cex` | 反例 → 结构化时序摘要（周期、信号、违反性质） |
| `read_design` | 查询模块端口、信号类型、子模块实例、连接展开 |

两级验证策略：

- **全局 BMC（筛选）**：完整大模块，深度浅（起点低，如 10）。
  BMC 有界语义下"通过"仅表示深度 k 内无反例；BOUND_SHORT 情景
  中假反例不会出现（未观察到违背即通过），窗口边缘失败标记待人工
- **模块级 IC3（完备定案）**：原子模块 + 已注入 assume 集，无界证明。
  IC3 超时 → `TIMEOUT_UNPROVED`，降级标注（"BMC k 步内成立 + 假设
  有效"），不阻塞整树；注意 cache 类模块的大数组是状态爆炸点
- **蕴含检查**：`∧children ⊢ parent` 编译为 `G(a -> c)` 走完备模式

## 6. 主循环

```
INIT:  读入 hierarchy + property
       classify_prop 校验（一致性门，拒绝即终止）
       输入性质初检（全局 BMC；REAL_BUG 仅可能在此阶段报告）
       proof_tree = {root}
LOOP (round ≤ N，默认 20):
  1. decomposer 分解 PENDING 节点（单策略：CONJUNCT 或 ASSUME）
     CONJUNCT 路线蕴含检查**先行**：children 入树后立即验证
     ∧children ⊢ parent（children 公式作 assumes 跑模块 IC3——纯逻辑
     蕴含，与 children 真假无关，分解方向错误在此早发现），通过标
     MOD_PROVEN，children 全部证毕后直接升级 IC3_PROVEN
  2. dispatcher 对 children 全局 BMC 筛选
       PASS → BMC_FILTERED
       FAIL → critic → 按 strategy 机械归因
         CONJUNCT → BAD_DECOMP，局部回滚
         ASSUME  → CONTRADICT_ASSUME，重设计 assume
  3. validator: 矛盾检查 + 无环检查
       ASSUME 路: assume（身份 1）写入目标模块性质文件作 IC3 前提，
         证明 A /\ Mᵢ |= P；同时该 assume 改释为 assert（身份 2）
         作为新验证目标自动挂树，其 strategy 固定为 CONJUNCT
         （禁止再走 ASSUME），其 children 全部验证完成才表明该
         assume 兑现（discharged）
       中间节点: 蕴含检查（完备模式）
       通过 → IC3_PROVEN；IC3 超时 → TIMEOUT_UNPROVED 降级
  4. 回溯:
       fail_count < 3 → 局部（重分解本节点 / 重设计 assume）
       fail_count ≥ 3 → 全局（回退父节点，失败历史保留）
       总轮数超限 → 熔断，输出证明树快照 + 未决清单，人工介入
EXIT:  根节点 PROVEN 且无 PENDING（自动挂树保证无悬空 assume）
       → 成功报告
```

## 7. 安全边界与项目布局

- **DUT 源码只读，性质文件可写**：agent 唯一可写的是各模块的 CHA
  性质文件（每子模块一个 `props/<Module>.cha`，条目带性质 ID 注释，
  回滚 = 删条目）
- decomposer 上下文预算：只给当前节点 + 相关模块接口摘要 + 失败历史
  （截断），防上下文膨胀

```
AGVerify/
├── DESIGN.md                 # 本文档
├── spec/                     # 输入层
│   ├── hierarchy.json
│   └── properties.json
├── proof_state/              # 全局状态（运行时维护）
│   ├── proof_tree.json
│   ├── signal_registry.json
│   ├── assumptions.json
│   └── failures.jsonl        # 失败历史（只追加）
├── agents/                   # LLM 角色定义
│   ├── decomposer.md
│   └── critic.md
├── tools/                    # 工具层（后续可包 MCP server）
│   ├── cha_verify.py
│   ├── parse_cex.py
│   └── read_design.py
├── scripts/                  # 程序模块
│   ├── classify_prop.py
│   ├── dispatcher.py         # 主循环
│   └── validator.py
├── props/                    # CHA 性质文件（每模块一个，agent 可写）
└── results/                  # 每轮快照、CEX、决策日志、最终报告
```

## 8. 实施序列

1. `classify_prop` 脚本（依赖最少，可单独测）
2. 手工对一条真实性质跑通 CHA 的 bmc / ic3 / 蕴含三种调用，
   固化 `cha_verify` 工具接口
3. proof_tree 数据结构 + dispatcher 主循环（先不接 LLM，人工决策驱动跑通）
4. 接入 decomposer + critic（LLM）
5. 端到端验证一条性质，然后扩展
