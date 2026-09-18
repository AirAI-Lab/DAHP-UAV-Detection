# Codex 科研协作指南

适用于研究者从初始想法开始，借助 Codex 推进代码实现、实验、论文写作、审稿答复和投稿准备。Codex 是工程与稿件流程助手；研究假设、科学解释、claim 选择、作者责任和投稿决定始终由研究者负责。

## 协作分工

Codex 可用于：

- 阅读仓库并提取客观事实；
- 设计受控实验矩阵；
- 编写研究代码、测试、队列脚本和评估脚本；
- 诊断失败 run；
- 将结果文件转换为表格和图；
- 检查稿件一致性；
- 格式化作者已核实的文献；
- 起草 point-by-point 审稿答复；
- 维护中英文项目文档；
- 准备可复现发布。

不应交给 Codex 决定：

- 科学假设；
- 最终 claim；
- 弱证据的解释；
- 文献真实性；
- 作者贡献与署名；
- 伦理、资助或利益冲突声明；
- 结果最终认可；
- 是否投稿。

## 项目启动提示模式

提供给 Codex：

1. 研究目标与非目标；
2. 数据集和标签；
3. 现有仓库路径；
4. 硬件与 GPU 配额；
5. baseline 与指标；
6. 已知限制；
7. 目标期刊；
8. 必需 artifacts；
9. 本次范围是代码、论文，还是二者同时。

示例：

```text
阅读 <repository>，先不修改文件，输出研究计划。
目标：...
非目标：...
数据集：...
主 baseline 与指标：...
硬件限制：...
目标期刊：...
首批交付：事实表、实验矩阵、可复现 baseline。
缺失值标 PENDING，不要推测。
```

要求 Codex 将假设与事实分开报告。

## 里程碑 1 — 诊断与研究计划

期望输出：

- 客观事实表；
- 数据审计；
- 候选混杂因素；
- 研究问题；
- 最小实验矩阵；
- baseline 复现计划；
- 风险与停止条件。

人工检查：

- 现象是否在正确分析单位上测量？
- 原因是否可分离？
- 哪些比较公平？
- 什么结果会证伪假设？
- 哪些 claim 超出证据范围？

## 里程碑 2 — 实现

要求输出：

- 配置 schema；
- train/eval 入口；
- smoke tests；
- resume 行为；
- 日志与结果 schema；
- 方法/代码一致性说明；
- 公有/私有路径分离。

推荐请求：

```text
实现 <feature> 并加测试。保持现有评估协议不变。
添加 run manifest，对无效标签或 GPU 绑定 fail fast。
若需要改变科学默认参数，先报告 diff 和理由。
```

审查 patch：

- 默认参数；
- device 绑定；
- seed；
- checkpoint resume；
- class mapping；
- 协议变化；
- 隐藏依赖；
- 被删除的日志。

## 里程碑 3 — 实验运维

给 Codex 明确权限和边界：

```text
最多使用 <N> 张 GPU。任务必须支持 checkpoint 恢复。
不得杀无关进程。每次 launch 写入 queue log。
若 epoch 重复、两次 OOM，或超过 <timeout> 没有结果，停止并报告。
```

要求状态报告包含：

- GPU/process map；
- 完成 epoch；
- best metric；
- 错误；
- ETA；
- 下一步。

不得把训练中的部分指标当最终证据。

## 里程碑 4 — 证据聚合

要求生成：

```text
claim | evidence file | protocol | n | uncertainty | status | action
```

让 Codex 标出：

- 混用协议；
- 输入尺寸不同；
- seeds 缺失；
- literature-only 比较；
- 无支持的因果表述；
- 图表旧值；
- pending 结果。

摘要和每条贡献都必须映射到证据行。

## 里程碑 5 — 稿件开发

提供事实表、证据矩阵、已核实文献、期刊模板和绘图脚本。要求按顺序起草：

1. Methods；
2. Results；
3. Discussion；
4. Introduction；
5. Abstract；
6. Conclusion。

约束示例：

```text
只使用给定 evidence file 中的数值，不得四舍五入到不同含义或重新解释。
不确定处写 TODO。Methods 保持事实，Results 表述受限。
术语一致。不得把 reproduced comparison 升级为 benchmark SOTA claim。
```

草稿后不要无结构重写，而要审计：

```text
列出每个事实 claim 及证据行；标出无支持 claim、混协议、术语不一致、
段落功能不清之处。
```

## 里程碑 6 — 审稿答复

每条意见要求 Codex 生成：

```text
Reviewer concern:
Manuscript location:
Technical classification:
New evidence required:
Changes made:
Limitation if evidence cannot be added:
Exact response text:
```

规则：

- 尊重且准确地复述 concern；
- 区分观点与技术事实；
- 可行时提供受控实验；
- 诚实报告负结果；
- 不承诺无法获得的 test GT；
- 引用修改后的稿件段落；
- 先更新证据矩阵，再写答复。

## 里程碑 7 — 投稿与发布

让 Codex 准备：

- 期刊 LaTeX build；
- 干净图源；
- supplementary tables；
- cover letter；
- highlights；
- graphical abstract；
- 复现说明；
- code release checklist；
- 结果 checksum；
- 中英文文档索引。

人工最终检查：

- 所有作者同意投稿；
- 文献核实；
- data/code statement 准确；
- 伦理、资助、利益冲突完整；
- 结果摘要与表格一致；
- 无私有信息。

## 安全协作习惯

| 风险 | 控制 |
|---|---|
| 无支持 claim | claim-evidence matrix |
| 混协议 | 协议分字段 |
| 润色改结果 | 固定数值列并 diff |
| 文献凭空生成 | 只输入已核实文献 |
| 隐藏代码变化 | 要求 patch summary 和测试 |
| 队列失控 | GPU 配额、lockfile、timeout |
| 私有路径泄漏 | 公开发布扫描 |
| 行文过长 | 段落功能表 |
| Discussion 重复 Intro | Results 后写，按机制组织 |
| 答复过于防御 | 复述 concern 并给证据 |

## 可复用状态请求

```text
按四部分汇报：
1. 已完成证据；
2. running/pending 实验；
3. 稿件同步状态；
4. blockers 与下一步。
每个数值给出协议和 evidence file。不得根据 pending run 泛化结论。
```

## 文档策略

重要项目文档同时维护英文和中文：

```text
FACT_TABLE.md / FACT_TABLE.zh-CN.md
EXPERIMENTS.md / EXPERIMENTS.zh-CN.md
REVISION_EVIDENCE_MATRIX.md / REVISION_EVIDENCE_MATRIX.zh-CN.md
PAPER_PROCESS_PLAYBOOK.md / PAPER_PROCESS_PLAYBOOK.zh-CN.md
```

两种语言使用同一结果源。结果变化时，必须在同一 commit 中更新两个版本。
