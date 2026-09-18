# DAHP 案例研究：从检测问题到可修订稿件

本参考将 DAHP UAV detection 项目浓缩为可复用模式，记录过程决策和证据演进，不包含私有基础设施细节。

## 1. 初始研究对象

项目起点是 UAV 图像中的三个耦合病理：

1. 极端目标尺度失衡；
2. 类别频率长尾；
3. 结构相似类别相互干扰。

早期结构模块在强 baseline 上没有稳定收益，且常使定位变差。因此项目从“添加模块”转为数据中心问题：

```text
rebalancing 何时有效？增益中多少来自曝光、数据量和 targeted 类别选择？
```

## 2. 建立客观画像

profiler 有意采用 label-only：

- 不解码图像；
- 不计算梯度；
- 不运行模型推理；
- 不依赖预测混淆矩阵。

输出包括：

- 类别频率与 head-tail 比；
- tiny/small/medium 目标比例；
- aspect-ratio 与尺度直方图重叠；
- structural-similarity graph；
- head-anchored confusion axis；
- resolution/backbone 与 oversampling policy。

这使 VisDrone 到 UAVDT 的迁移无需数据集级代码修改。

## 3. 修正方法-代码-论文一致性

早期发现关键不一致：

- 论文曾将 confusion score 描述为 geometric/co-occurrence 组合；
- 实现实际使用 aspect-ratio 与 scale histogram intersection。

项目暂停扩实验，直到论文、代码、图和验证脚本统一为：

```text
0.6 * aspect-ratio overlap + 0.4 * scale overlap
```

教训：增加实验前，先确认论文声称的测量就是代码实现的测量。

## 4. 从大量 run 到受控机制

项目曾积累大量结构与采样尝试。最终不做事后挑最优，而重组为受控 arm：

1. architecture/resolution ladder；
2. tail-only sampling；
3. confusion-axis sampling；
4. union sampling；
5. random volume control；
6. exposure-matched baseline；
7. cross-dataset transfer；
8. online prediction probe。

这把工程排行榜转化为 regime principle 的证据。

## 5. 负结果成为贡献

失败结果被保留并审计：

- 七代 feature module；
- head-decouple 与 weight-share 变体；
- naive allocator；
- 1280 frequency sampling；
- full-image 模型上的切片推理；
- SAFT mixture；
- 较短 YOLO26 probes。

它们支持一个范围明确的结论：在匹配预算下，这些 feature-level 干预没有提升强 baseline，且常恶化定位。负结果没有隐藏，而是定义了 data-space policy 的动机。

## 6. 分辨率与结构分离

完整 YOLOv8l / YOLOv8l-P2 ladder 分离结构与分辨率：

| Detector | 640 | 1280 | 1600 |
|---|---:|---:|---:|
| YOLOv8l | 23.21 | 33.76 | 37.94 |
| YOLOv8l-P2 | 27.21 | 37.96 | 39.04 |
| P2 gain | +4.0 | +4.2 | +1.1 |

因此最终系统不能称为“零结构变化”：P2 是被消融的结构选择；非侵入的是 sampling policy。

## 7. 发现 exposure moderator

关键表面结果是：

```text
1920 px union - base = +3.83 AP
```

审稿式质疑是：union 是否只是增加曝光？于是加入 120-epoch exposure-matched baseline：

| Arm | native AP | md100 AP | APs |
|---|---:|---:|---:|
| base@60 | 35.67 | — | — |
| union@60 | 39.50 | 37.93 | 30.46 |
| base@120 | 39.01 | 37.51 | 29.54 |

匹配 residual 为：

```text
+0.49 native AP
+0.42 md100 AP
+0.92 APs
```

这 refined 了原理：1920 px 是 exposure-limited，same-epoch 增益不能全归因 targeted sampling。

## 8. Volume 与 targeted reallocation

1600 px 的 random-volume control 分离数据量与 targeted union：

| Arm | n | AP |
|---|---:|---:|
| R only | 3 | 36.55 ± 0.21 |
| random volume | 5 | 36.91 ± 0.29 |
| targeted union | 3 completed | 37.09 ± 0.16 |

当前解释：

```text
volume:       +0.36 AP
targeted:     +0.18 AP
```

该结果诚实但未最终收口；targeted union 正在扩展到 5 seeds，之后才使用显著性表述。

## 9. 让原理具备预测性

单 run epoch-gain 规则无法在线区分 regime，被作为 negative control 报告。成功诊断是 two-arm early probe：

- 只用前若干 epoch；
- 比较 treatment 与 matched base；
- 使用 best-checkpoint gap；
- epoch 30 probe。

结果：

```text
Pearson r = 0.983
5/5 regime separation
threshold = 2.5 AP
```

这使工作从事后命名 regime 变为可预测 principle。

## 10. Baseline 公平性演进

对比表演化为三层：

1. 同输入 general detectors；
2. UAV-specific detectors；
3. 同 detector mechanism controls。

Modern baselines 包含 YOLO11、YOLO12、YOLO26。640 px：

```text
DAHP-M 26.11
YOLO26-L 24.90
YOLO12-L 23.67
YOLO11-L 23.97
```

文献值与复现值分开标注。未公开发表的高分辨率 comparator claim 从主证据中删除。

## 11. 稿件同步

每个完成实验都会同步：

- fact table；
- evidence matrix；
- main table；
- ablation table；
- regime matrix；
- figure generation script；
- figure caption；
- discussion；
- conclusion；
- public repository。

Pending 结果不进入最终 claim。这防止了看似漂亮但无支持的叙事进入稿件。

## 12. 可复用经验

| 经验 | 迁移方式 |
|---|---|
| 先测量再干预 | label/data profile 揭示 scale、tail、confusion |
| 每次只检验一个因素 | structure、resolution、volume、targeted policy 分离 |
| 加 random-volume control | 区分“更多数据”和“选哪些数据” |
| 因果 claim 前匹配曝光 | 高分辨率 oversampling 必需 |
| 保留失败模块审计 | 负结果可定义 research gap |
| 不混协议 | md100 与 native 分列 |
| 使用 online probe | 避免事后 regime 归类 |
| 标记 pending evidence | 防止部分 run 变成结论 |
| 中英文文档同步 | 便于团队审查与交接 |
| 发布绘图脚本 | 图可审计 |

## 13. 下一个项目的模式

1. 定义现象与非目标。
2. 建立 label/data profile。
3. 在同一 evaluator 下复现强 baseline。
4. 建立 architecture/resolution ladder。
5. 加入 policy arms 与 random controls。
6. 加 exposure 或预算匹配 controls。
7. 检验在线可预测性。
8. 不调参迁移到第二个数据集。
9. 加 modern 与 domain baselines。
10. 用 evidence files 审计每个 claim。
11. 先写 Methods/Results，再写 Introduction。
12. 用实验而非修辞回应审稿。
