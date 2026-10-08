# AGVerify 验证运行总结模板

> 每次验证运行结束后复制本模板到对应 run 目录, 命名
> `results/run_<时间戳>/SUMMARY.md`, 按实况填写。
> 数据来源: report.json / llm_calls/*/ / sbt/*.log /
> final_proof_state.json

## 运行信息

| 项 | 值 |
|---|---|
| run 目录 | run_YYYYMMDD_HHMMSS |
| 目标性质 | `<id>: <formula> @ <module>` |
| 先验 | `<priors.json 条目数与模块>` |
| LLM | `<模型 @ base_url, temperature>` |
| 起止/耗时 | `<时间, 总时长>` |
| 结局 | SUCCESS / ABORTED / ROUNDS_EXHAUSTED / 被停 |
| KB 产出 | `<定理数与列表>` |

## 每轮记录

> 每轮一行。列含义:
> - 轮次目标: 本轮处理的节点(性质/assume/兑现)与所处阶段
>   (分解/全局BMC/模块IC3/蕴含/兑现)
> - agent 决策: decomposer 输出(strategy + children/assumes 公式摘要)
> - critic 反馈: 失败时的归因与 hint 摘要
> - BMC/IC3 结果: PASS / FAIL(第几拍) / ERROR(编译/语法/超时) / 未到达

| 轮 | 轮次目标 | agent 决策 | critic 反馈 | BMC | IC3 | 结局与去向 |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| ... | | | | | | |

## 失败分析

- 阻断性错误(编译/工具/框架 bug): `<错误内容, 根因, 是否已修>`
- 分解质量问题(退化/循环/偏离): `<现象与改进方向>`

## 结论与遗留

- 本轮学到: `<对 prompt/框架/先验的调整建议>`
- 待修问题: `<清单>`
