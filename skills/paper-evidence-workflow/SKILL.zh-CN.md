# 论文证据工作流

维护从原始实验记录到稿件每个论断的完整证据链，绝不让叙事超过证据。研究者负责假设、解释、claim、署名决定和最终批准。

## 语言入口

- English: [SKILL.md](SKILL.md)
- 简体中文：[SKILL.zh-CN.md](SKILL.zh-CN.md)

## 参考文档路由

只阅读当前模式需要的参考文档：

- **新项目或完整“论点—论文”过程**：`references/research-lifecycle.md` / `references/research-lifecycle.zh-CN.md`
- **研究代码、队列、checkpoint、服务器与发布工程**：`references/experiment-code-ops.md` / `.zh-CN.md`
- **与 Codex 从想法推进到投稿**：`references/codex-research-collaboration.md` / `.zh-CN.md`
- **DAHP 项目历史和可复用经验**：`references/dahp-case-study.md` / `.zh-CN.md`
- **可直接复制的表格与检查清单**：`references/artifact-templates.md` / `.zh-CN.md`

重要项目文档必须同时维护英文和中文。结果变化时，两种语言版本必须在同一个 commit 中更新。

## 必需项目工件

在实质性写作或实现前创建：

1. **事实表**：数据集/split、数量、模型、checkpoint 来源、硬件、包版本、schedule、batch、seed、指标定义、评估协议、latency 协议、已完成/待完成结果和偏差。
2. **文献证据矩阵**：已核实 citation key、确切发现、benchmark/split、输入尺寸、协议和局限。
3. **实验矩阵**：研究问题、假设、treatment、control、固定变量、指标、seed 策略、决策规则和失败模式。
4. **Claim-evidence 矩阵**：稿件句子、证据文件/表/图、协议、不确定性、状态和后续行动。
5. **Run 状态板**：活跃和已完成 run、epoch、best/final 指标、进程状态、结果文件更新时间和预期论文用途。
6. **投稿检查表**：稿件、补充材料、cover letter、声明、代码、数据可用性和复现说明。

未知事实标记 `PENDING`，绝不推测。不可比较的协议必须分字段保存。

## 研究与实验设计

- 写出全文必须证明的一句话论点。
- 从该论点推导研究问题；每个实验必须回答一个问题或刻画边界条件。
- 分离架构、输入分辨率、容量、训练曝光/数据量、targeted policy、评估器和 schedule。
- 使用三层比较：
  1. 同协议 general baselines；
  2. 领域 baselines，并标注 reproduced / literature / official weights；
  3. 同 detector 消融和机制控制。
- 为每个 baseline 记录 split、输入尺寸、epochs、batch、硬件、checkpoint 来源、参数/FLOPs、评估器、协议和偏差。
- 当数据复制或 schedule 变化可能解释增益时，加入 volume-matched 与 exposure-matched controls。
- 尽可能报告 n、mean、standard deviation 和 paired differences；没有有效检验和效应量时避免使用显著性表述。
- 各 arm 使用相同的 checkpoint 选择规则。

## 写作与修订顺序

1. Methods：只写事实表和代码中存在的内容。
2. Results：每段一个受控发现；说明效应和边界。
3. Discussion：机制、与先前工作比较、局限和范围。
4. Introduction：病理、gap、有限贡献和核心结果。
5. Abstract 与 conclusion：只复用已被支持的 claim。
6. Cover letter 与补充材料。

对审稿意见建立 response matrix：concern、类型、稿件位置、所需证据、修改内容、limitation 和确切回复。可行时用受控实验而不是修辞回应。

## Claim 与公平性审计

对每个事实性句子核实：

- 数值来源；
- 评估协议；
- split；
- 输入尺寸；
- schedule 和曝光；
- reproduced 还是 literature-only；
- 相减是否有效；
- n 和不确定性；
- “state of the art”、“causes”、“significant”、“architecture-free” 是否有依据。

没有证据行的 claim 要删除，或补充对应实验。Pending 证据不得进入最终结论。

## 图、表与代码审计

- 每个 figure panel 只表达一个信息；caption 说明比较对象和控制变量。
- 绘图数据来自与表格相同的结果文件。
- 术语、单位、缩写、类名和协议标签一致。
- 公式、代码默认值、稿件参数和公开配置一致。
- 图/表脚本入库，并在结果缺失时报错。
- seed、resume 行为、评估器和环境可复现。
- 公开版本不包含私有路径、凭据、内部 ID 或未说明的机器特定假设。

## 最终质量门禁

- [ ] abstract 和 contribution 的每个 claim 都有证据行；
- [ ] pending 项未进入最终 claim；
- [ ] 没有混合协议相减；
- [ ] baseline 偏差已披露；
- [ ] 统计表述与 n 和检验一致；
- [ ] 公式与实现一致；
- [ ] 图表与原始结果一致；
- [ ] 文献已核实且引用范围正确；
- [ ] LaTeX 编译两次，无 error、未解析引用或 overfull box；
- [ ] supplement、代码、数据声明和复现说明完整；
- [ ] 中英文档已同步。
