# AGVerify 配置参数说明（config.json）

所有参数在 `proof_state.py` / `cha_verify.py` 启动时读取；文件不存在则
使用内置默认值。函数显式传参时覆盖 config（config 是默认值层）。

## 回溯与循环防护

- **rollback_max_fail**（默认 3）
  单节点失败次数阈值。`fail_count >= 此值` 时 record_failure 返回
  "global"，回溯从局部（重分解本节点）升级为全局（回退父节点，
  失败历史保留）。

- **max_discharge_depth**（默认 3）
  assume 兑现链嵌套深度上限（A1 兑现中提出 A2、A2 兑现中提出 A3…）。
  超过则 add_assume 拒绝并提示改走 CONJUNCT——兜住签名检查查不出的
  换写法语义循环。

- **max_rounds**（默认 20）
  整个验证流程的总轮数熔断，超过即中止并输出证明树快照与未决清单，
  人工介入。

## BMC（全局筛选）

- **bmc_bound**（默认 20）
  `cha_verify(mode="bmc")` 的默认深度，映射 `BoundedCheck(k)`——从
  复位起检查 k 个周期。窗口过小时性质不会误报失败（未观察到违背即
  通过），调大只会更严格。

- **bmc_timeout_sec**（默认 600）
  BMC 模式下单次 sbt 调用的超时秒数。

## IC3（模块级完备证明）

- **ic3_iters**（默认 20）
  `cha_verify(mode="ic3")` 的默认迭代次数，映射 `Ic3Check(k)`——IC3
  逐步迭代求上近似的迭代上限（非 BMC 的深度语义）。

- **ic3_timeout_sec**（默认 1800）
  IC3 模式下单次 sbt 调用的超时秒数。IC3 可能长时间不收敛，此参数
  是 TIMEOUT_UNPROVED 判定的来源之一；显著大于 bmc_timeout_sec。

## 流程开关

- **compile_check**（默认 true）
  跑求解器前是否先执行 `testOnly mini.AGTileSignal` 编译检查（不合法
  信号/编译错误前置拦截）。设 false 跳过（省一次 sbt 启动，错误晚发现）。
