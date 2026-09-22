# 发布的结果摘要

`paper_results_public.json` 是论文使用的 sanitized numerical-evidence 文件，
包含评估指标、控制实验聚合、复现 modern baseline、负结果审计、回顾性
early-signal 数据以及最终 latency/memory 审计。该文件不包含预测框、
checkpoint、PID、GPU UUID、机器特定路径或本地实验标识。

`profile_threshold_sensitivity.json` 与 `uavdt_threshold_sensitivity.json`
包含 label-only 策略决策审计。它们不估计 AP。

未发布的原始预测、checkpoint 与评估 artifact 不随仓库分发。可按文档运行
评估脚本生成同协议输入。
