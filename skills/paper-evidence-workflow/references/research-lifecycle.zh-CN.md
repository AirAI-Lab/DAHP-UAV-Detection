# 端到端科研生命周期

适用于从研究想法开始，推进到代码实现、实验、论文撰写、审稿修订直至发表后的维护。

## 阶段 0 — 定义研究对象

写代码或正文前，先记录：

1. **现象**：观察到什么失败？
2. **分析单位**：数据集、图像、类别、训练 run，还是部署场景？
3. **候选原因**：数据分布、模型容量、优化、评估协议，还是部署偏移？
4. **干预方式**：能改变什么？
5. **非目标**：不准备声称什么？
6. **成功标准**：定量的、协议明确的指标。

先写一句话论点：

```text
我们检验 <受控干预> 是否在 <协议> 下提升 <任务指标>，
并同时分离 <混杂因素>。
```

写不出这句话，说明项目还不适合进入实现。

## 阶段 1 — 建立客观事实表

先于论文建立事实表，只记录能从代码、日志、数据元信息和评估记录中观察到的信息。

最少字段：

- 数据集与版本；
- train/validation/test split；
- 每个 split 的图像数和实例数；
- 标签体系与类别映射；
- 预处理与增强；
- 模型、checkpoint 来源、参数量、FLOPs；
- optimizer、learning-rate schedule、batch、epochs、seeds、GPU 数；
- evaluator、指标定义、maxDets、IoU 阈值、面积区间；
- latency 协议；
- 已完成结果；
- pending 结果；
- 与匹配预算的偏差。

未知值写 `PENDING`。缺失比推测更安全。

## 阶段 2 — 建立文献证据矩阵

只使用从出版社页面、DOI、arXiv 版本或可信文献管理器核实过的文献。每条记录：

- 借用的确切结论；
- 数据集和 split；
- 输入分辨率；
- 已报告的训练预算；
- 评估协议；
- 代码/权重是否可用；
- 局限；
- 将用于论文哪一节。

区分：

1. 文献报告值；
2. 我们复现值；
3. official weights 评估值；
4. challenge/test-server 值。

不得跨类别直接相减。

## 阶段 3 — 设计实验矩阵

每个研究问题都应有：

| 字段 | 含义 |
|---|---|
| RQ | 推进核心论点的问题 |
| Hypothesis | 可证伪假设 |
| Treatment | 被改变的因素 |
| Control | 匹配对照 |
| Fixed variables | 其他保持不变的因素 |
| Metric | 主指标与次级指标 |
| Sample size | seeds 或独立运行数 |
| Decision rule | 什么结果支持或反驳假设 |
| Expected failure | 什么情况会使解释失效 |

实验只为了关闭 RQ、刻画边界或回答合理审稿问题；不要为了增加表格长度而堆方法。

## 阶段 4 — 可复现实现

先建立 run manifest，而不是一次性 notebook。

推荐结构：

```text
configs/         数据与实验配置
scripts/         构建、训练、评估、聚合、绘图
src/             方法实现
tests/           smoke 与一致性测试
docs/            中英文事实表、证据表、过程文档
results/         评估摘要与 manifest
paper/           论文源码与图
```

规则：

- 一个实验对应不可变名称和配置；
- 每个 run 写入参数、checkpoint、指标、环境和 git commit；
- 评估独立于训练代码；
- 显式设置随机种子；
- 训练中指标不替代最终评估；
- 图由结果文件生成，不手填数值。

## 阶段 5 — 运行受控实验

启动前检查：

- GPU 绑定；
- checkpoint resume；
- schedule 与 batch；
- dataset YAML；
- class ID 与名称；
- evaluator 协议；
- checkpoint 大小；
- 磁盘容量；
- 重启恢复；
- 日志路径。

运行中跟踪：

- 已完成 epoch；
- best/last 指标；
- 进程运行时间；
- GPU 利用率与显存；
- results 文件更新时间；
- 需要干预的错误。

判断 stalled run 要同时看进程与产物，不能只看进程是否存在。

## 阶段 6 — 聚合证据

每个完成 run 提取：

- 主指标；
- 次级指标；
- per-class 结果；
- 面积指标；
- 跨种子不确定性；
- best epoch；
- final epoch；
- latency 与参数量；
- 协议；
- 配置哈希；
- 偏差。

存为 JSON/CSV，再生成表格和图。md100/native、val/test-dev、best/final 必须分字段保存。

## 阶段 7 — 撰写论文

推荐顺序：

1. Methods；
2. Results；
3. Discussion；
4. Introduction；
5. Abstract；
6. Conclusion；
7. Cover letter。

Methods 只能写事实表或代码中存在的内容。Results 每段说明受控比较、数值结果、不确定性和边界。Discussion 解释机制与局限，不重复 Introduction。

## 阶段 8 — 审稿修订

对每条审稿意见：

1. 复述技术 concern；
2. 分类为方法、证据、统计、公平性、表述或范围；
3. 定位稿件位置；
4. 判断需要补实验、改表述还是写 limitation；
5. 增加 claim-evidence row；
6. 更新正文和补充材料；
7. 编译与交叉检查；
8. 撰写 point-by-point response。

可行时，不用纯文字回应方法学质疑，而用受控实验回应。

## 阶段 9 — 准备投稿

投稿包：

- 期刊模板正文；
- supplementary tables/figures；
- cover letter；
- highlights；
- graphical abstract；
- author contributions；
- funding；
- conflict of interest；
- data availability；
- code release；
- 复现说明；
- 带 checksum 的结果摘要。

投稿前重跑 claim-evidence audit 和 LaTeX 检查。

## 阶段 10 — 发表后维护

维护：

- 与论文对应的 release tag；
- 冻结结果摘要；
- 环境文件；
- 运行说明；
- issue template；
- changelog；
- 论文表格到结果文件的映射。

当其他研究者无需内部文件即可复现评估流程并验证每个 claim 时，论文工程才算完整。
