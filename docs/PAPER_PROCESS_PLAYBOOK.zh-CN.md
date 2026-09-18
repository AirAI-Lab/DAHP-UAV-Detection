# SCI 论文全过程复用手册（DAHP 项目版）

本文档沉淀 DAHP 论文从问题定义、实验设计、审稿回应到投稿包制作的完整流程，并吸收《用 Codex 完成一篇可投稿级 SCI 论文》的核心方法：<https://mp.weixin.qq.com/s/aKgnnLhW46P6Y_NkxHDJxA>。

核心原则：

> AI 负责整理、结构化、核查、排版和追踪证据；科研假设、实验设计、数据解释、创新判断和最终结论必须由作者负责。AI 不能替我们做科学结论。

## 0. 论文工作总原则

1. **事实先行**：先建立客观事实表，再写引言和结论。
2. **证据先行**：每个数字必须能追溯到实验 JSON、表格或已核实文献。
3. **控制变量先行**：架构、分辨率、曝光量、采样策略必须拆开验证。
4. **公平性优先于榜单**：同 split、同协议、同预算优先；文献值只作上下文。
5. **结论受限**：宁可写受限但严密的结论，不写过强但容易被审稿人推翻的 SOTA 声明。
6. **可复现**：代码、配置、种子、评估脚本、结果摘要应可发布。
7. **AI 只做审计**：不能编造参数、文献、实验结果或科学解释。

## 1. 第一阶段：建立事实表

先不写引言，先写 `docs/FACT_TABLE.md`。

事实表至少包含：

- 任务目标；
- 数据集、split、类别体系、预处理；
- 训练/验证/测试图像数和实例数；
- GPU、CUDA、PyTorch、Ultralytics 版本；
- 模型结构、checkpoint 来源、参数量；
- optimizer、learning rate、batch、epochs、seed；
- 数据增强；
- 指标定义和评估协议；
- latency 测试协议；
- 已完成结果；
- 未完成结果；
- 已知偏差。

规则：

- 缺失项写 `PENDING`，禁止推测；
- 每个结果绑定到 run 或 JSON；
- 不同协议分开列，不能混用相减；
- 每次实验更新后同步事实表；
- 论文写作只能引用事实表中的固定事实。

模板：

```markdown
| 项目 | 事实 | 来源 | 状态 |
|---|---|---|---|
| 数据集/split | ... | dataset yaml | fixed |
| 训练预算 | ... | args.yaml | fixed |
| 指标 | ... | eval script | fixed |
| 主结果 | ... | results/eval/*.json | complete/pending |
```

## 2. 第二阶段：文献证据矩阵

不要让 AI 自由检索并生成参考文献。正确流程：

1. 作者在 Zotero、IEEE Xplore、arXiv、PubMed 或出版社页面确认文献；
2. 保存 BibTeX/key；
3. 再让 AI 只做映射和格式化。

矩阵模板：

| 论文论点 | 文献 key | 证据类型 | 实验设置 | 局限 | 正文用途 |
|---|---|---|---|---|---|
| UAV 图像小目标密集 | `visdrone` | 数据集论文 | VisDrone | split/协议可能不同 | Introduction |
| cropping 提高有效像素 | `clusdet`, `dmnet` | 方法论文 | UAV benchmark | 同时改变 cropping 和 detector | Related Work |

核查规则：

- 无 DOI 或稳定 URL 不进入正文；
- 未公开发表的高分辨率 claim 不作为主证据；
- 区分 val、test-dev、challenge；
- 记录输入尺寸和训练预算；
- 引用强度不能超过原文献实验支持范围。

## 3. 第三阶段：一句话论点

先写出全文必须证明的一句话。DAHP 当前版本是：

> Label-only profiling can identify when non-invasive UAV-detection
> rebalancing helps, but the effect is regime-dependent and must be separated
> from architecture, data volume, and exposure.

中文理解：

> 标签级数据画像可以判断非侵入式重采样何时有效，但其效果依赖训练 regime，并且必须与架构、数据量和曝光量分离。

用这一句话检查：

- 标题；
- 摘要；
- 贡献；
- 图表；
- 结论。

如果某段不支持这句话，删除或移动到补充材料。

## 4. 第四阶段：实验设计矩阵

每项理论创新必须对应一个可证伪实验。

模板：

| 研究问题 | 假设 | Treatment | Control | 固定变量 | 指标 | 种子 | 判断规则 |
|---|---|---|---|---|---|---|---|
| 增益是否来自曝光？ | 曝光匹配后增益缩小 | union@60 | base@120 | 模型/图像/评估器 | AP/APs | >=3 | 同时报告 same-epoch 和 matched |
| targeted 是否有残差？ | targeted > random | union farm | random volume farm | 模型/epochs/图像数 | AP/tail AP | 5 | mean/std/paired |

实验停止条件：

1. 研究问题已有受控实验支持；
2. 明确写成 limitation；
3. 明确写成 future work，且不用于当前结论。

不要为了“看起来完整”无限加实验。

## 5. 公平对比设计

### 5.1 Baseline 分层

不要把所有方法堆进一张大表。建议三层：

1. **General real-time detectors**
   - YOLOv8 / YOLO11 / YOLO12 / YOLO26 / RT-DETR；
   - 尽量同 640 输入、同 100 epochs。
2. **UAV-specific detectors**
   - QueryDet、CEASC、ClusDet、DMNet、UFPMP-Det、TPH-YOLOv5、UAV-DETR、RemDet；
   - 可复现的标 Rep.，文献值标 Lit.。
3. **Ablation / mechanism controls**
   - 同一 detector family；
   - 架构、分辨率、曝光、采样分别拆开。

### 5.2 每行必须记录

- 数据集和 split；
- 输入尺寸；
- epochs；
- batch 和 GPU 数；
- checkpoint 来源；
- 是否 pretrained；
- 参数量 / FLOPs；
- 种子数；
- 评估协议；
- Rep. 还是 Lit.；
- 偏差说明。

无法完全匹配时，必须在 caption 或 footnote 说明，不能做 algorithm-only 归因。

## 6. 统计规范

关键 treatment/control 建议：

- 至少 5 seeds；
- 报告 mean、std、n；
- 尽量做 paired seed-wise difference；
- 最终主张给 95% CI；
- 没有检验不要写 significant；
- 区分实际增益和统计不确定性；
- best-checkpoint 规则必须一致。

DAHP 当前注意点：

- random volume control 已 n=5；
- targeted union 已完成 n=3，两个额外 seed 正在跑；
- 在 n=5 完成前，不能写 statistically significant。

## 7. 写作顺序

推荐顺序：

1. Methods；
2. Results；
3. Discussion；
4. Introduction；
5. Abstract；
6. Conclusion；
7. Cover letter。

原因：Methods 和 Results 事实最稳定；Introduction 和 Abstract 应最后概括。

### 段落功能表

| 章节 | 段落功能 | 允许输入 |
|---|---|---|
| Intro 1 | UAV 检测病理 | 已核实文献和数据事实 |
| Intro 2 | 现有方法缺口 | 文献证据矩阵 |
| Intro 3 | 本文贡献和有限核心结果 | 事实表 |
| Methods | 可复现 profiler/policy | 代码和事实表 |
| Results | 主表、消融、控制实验 | 评估 JSON |
| Discussion | 机制、边界、局限 | 受控对比 |
| Conclusion | 受限总结 | 证据矩阵 |

## 8. 图表质量门禁

每张图必须满足：

- 每个-panel 一个明确信息；
- 术语与正文一致；
- 协议与对应表格一致；
- 有多种子时显示误差；
- 尽量使用矢量 PDF；
- 最终栏宽下字体可读；
- 不出现内部 run ID；
- 缩写有定义；
- caption 写清比较对象和控制变量；
- 绘图脚本入库。

DAHP 推荐图组：

1. 数据病理画像；
2. 方法流程；
3. 架构/分辨率 ladder；
4. regime matrix；
5. attribution waterfall；
6. online prediction；
7. per-class radar；
8. qualitative results。

## 9. Claim-Evidence 审计

投稿前建立 `docs/REVISION_EVIDENCE_MATRIX.md` 和 `docs/claim_evidence.csv`。

审计摘要、贡献、结果、讨论、结论中的每句话：

| 正文 claim | 精确证据 | 协议 | 状态 |
|---|---|---|---|
| ... | ... | ... | supported/pending/remove |

规则：

- 没有 row 的 claim 删除；
- pending 不能写成结论；
- 混协议的 claim 删除；
- 比输入尺寸不一致的 algorithm-only claim 删除；
- 文献值不能直接与我们 Rep. 值相减。

## 10. 一致性检查清单

每次修改论文后：

1. pdflatex 编译两次；
2. 无 LaTeX error；
3. 无 undefined reference；
4. 无 overfull box；
5. 图表交叉引用正确；
6. 数值没有意外变化；
7. 术语一致；
8. Methods 公式与代码一致；
9. 脚本默认参数与论文一致；
10. 图中数据与表格一致；
11. 文献作者、题目、venue、年份、页码、DOI 完整；
12. supplementary 被正文引用；
13. 删除内部实验 ID；
14. 检查 AI 使用声明。

## 11. 可复用 AI Prompt

### 事实抽取

```text
Read the supplied code, configs, logs, and evaluation JSONs. Extract an
objective fact table containing dataset, split, model, training budget,
evaluator, hardware, metrics, and uncertainty. Mark missing fields as PENDING.
Do not infer or invent values. For every fixed value, cite the source file.
```

### Claim 审计

```text
Compare the abstract, contributions, results, discussion, and conclusion.
List every factual claim and map it to a table row, figure, equation, or
evaluation JSON. Flag unsupported claims, mixed protocols, different input
sizes, or language stronger than the evidence.
```

### 公平性审计

```text
For every baseline row, list split, input size, epochs, batch, hardware,
checkpoint source, evaluator, and protocol. Identify whether the comparison is
same-protocol, reproduced, or literature-only. Suggest exact wording that
avoids overclaiming.
```

### 图表审计

```text
Inspect each figure caption and data source. Check terminology, units, panel
purpose, legend, font size, and whether plotted values match a table. Report
problems and suggested fixes; do not silently change scientific content.
```

### 文献审计

```text
Use only supplied verified references. Check authors, title, venue, year,
pages, DOI, and publisher/arXiv URL. Report mismatches or missing fields. Do
not create new references.
```

## 12. 服务器与实验管理

本项目形成的服务器规范：

1. 一个实验绑定一张 GPU；
2. 显式传 `--device N`，不能只依赖 `CUDA_VISIBLE_DEVICES`；
3. 每个实验必须有 checkpoint resume；
4. queue 脚本启动前检查 epochs 和进程状态；
5. `@reboot` crontab 自动恢复 supervisor；
6. logs 放 `logs/`，评估放 `results/eval/`；
7. 严格遵守 GPU 配额；
8. 用进程时间、results.csv mtime、GPU util/memory 判断 stall；
9. checkpoint 完成立即评估；
10. 训练中指标不能回填论文。

## 13. 投稿包清单

- [ ] 期刊模板主文；
- [ ] cover letter；
- [ ] highlights；
- [ ] graphical abstract；
- [ ] author contributions；
- [ ] competing interests；
- [ ] data availability；
- [ ] code release；
- [ ] supplementary tables；
- [ ] per-class results；
- [ ] negative-result audit；
- [ ] AI-use declaration；
- [ ] reference export；
- [ ] figure source scripts；
- [ ] reproducibility instructions；
- [ ] result summary checksums。

AI 使用声明模板：

```text
During preparation of this work, the authors used Codex (OpenAI) to assist
with organizing experimental records, checking manuscript consistency,
formatting tables and references, and drafting process documentation. The
authors reviewed and edited all content, verified all experiments and
citations, selected the scientific claims, and take full responsibility for
the content of the article.
```

## 14. 常见坑与修复

| 坑 | 修复 |
|---|---|
| AI 润色时改数值 | number-lock prompt；修改前后 diff 审核 |
| md100 和 native 混用相减 | 分开列、分开表 |
| same-epoch 曝光误当 targeted | 加 random volume 和 exposure-matched control |
| 分辨率和算法同时变化 | 用 ladder 和同输入消融 |
| 用异质文献值声称 SOTA | 写 strongest reproduced comparator under protocol |
| 种子少却写 significant | 增加 n 或只报告 mean/std |
| 公式和代码不一致 | verification script + JSON |
| Discussion 重复 Intro | Results 定稿后再写 Discussion，并按机制组织 |
| 图好看但信息不清 | 每个 panel 一个结论，绘图脚本入库 |
| 内部 run 名泄漏 | 发布前映射成科学名称 |

## 15. DAHP 项目实际路线

1. 标签级诊断：scale、long-tail、structural overlap；
2. 复现 baseline；
3. architecture ladder 分离 P2、容量、分辨率；
4. 比较 tail、confusion、union、allocator；
5. 加 random-volume 和 exposure-matched control；
6. 提出 exposure-aware regime principle；
7. 用 two-arm probe 做在线预测；
8. UAVDT 零调参迁移；
9. 补 modern baseline 和 negative-result audit；
10. 每次实验完成后同步论文、代码、图表和证据表。

这个路线可直接迁移到其他 data-centric detection 论文。
