# 实验协议

## 公平比较规则

1. 在算力允许的情况下尽量匹配 epoch 和 batch 预算；所有偏差在论文中明确披露。
2. 使用双重评估协议：COCO 风格 `maxDets=100`（md100，用于消融和主表公平协议）与 `maxDets=300`（native/Ultralytics 协议）。两者分开报告，避免协议挑选。
3. 区分复现值与文献值：外部方法标注为 `Lit.`（论文报告值）或 `Rep.`（在我们声明的条件下复现）。无法用公开权重复现的高分辨率文献值不作为主要证据。
4. 关键设置进行多种子实验。当前 random-volume control 为 5 个种子，targeted union 正在从 3 个种子扩展到 5 个种子。报告样本数、均值和标准差。
5. 提出的采样策略本身不改变网络结构、损失函数或推理过程。P2 结构选择单独披露并单独消融。

## 分辨率-regime 阶梯

对每个分辨率（640 / 960 / 1280 / 1600 / 1920）训练 base 模型和匹配 epoch 的 union-sampling 变体，用 dAP 随分辨率的变化刻画训练 regime：

| 分辨率 | same-epoch union dAP | 解释 |
|---:|---:|---|
| 640 | +0.21 | learnability 下界；目标相对 stride 过小 |
| 960 | +3.15 | under-fitted；额外曝光可以转化为学习收益 |
| 1280 | 约 0 | saturated；类别重分配近似零和 |
| 1600 | +0.78 | intermediate；volume 与 targeted 均有正贡献 |
| 1920 | +3.83 | exposure-limited；same-epoch 增益主要来自曝光 |

1600 px 的 md100 分解为：

```text
R only              36.55 ± 0.21
random volume       36.91 ± 0.29
targeted union      37.09 ± 0.16
```

即 volume 贡献约 `+0.36 AP`，targeted residual 约 `+0.18 AP`。

1920 px 的曝光匹配控制为：

```text
base@60             native 35.67
union@60            native 39.50 / md100 37.93
base@120            native 39.01 / md100 37.51
matched residual    native +0.49 / md100 +0.42 / APs +0.92
```

因此，1920 px 的 `+3.83 AP` 不能解释为 targeted sampling 本身的效果；其中大部分来自额外曝光。

## UAVDT 迁移

同一 profiler 和 union-sampling 策略在不重新调参的情况下应用于 UAVDT。过采样类别为 `{truck, bus, van}`：

| 配置 | AP | Tail |
|---|---:|---:|
| base | 37.86 | 32.05 |
| frequency-only | 37.80 | 31.49 |
| union | 38.55 | 33.73 |

结果为整体 `+0.69 AP`，尾类 `+1.69 AP`；frequency-only 无效，符合 regime 预测。

## 负结果披露

- 对 full-image 训练模型直接使用切片推理：`-2.3` 到 `-2.6 AP`。
- 1280 px frequency-only sampling：接近 0 增益，符合饱和 regime。
- 简单 allocator 低于 union：`38.51 < 38.85` native AP。
- 七代 feature-module 实验：`-0.7` 到 `+0.1 AP`，验证 DFL 增加 `+0.05--0.08`。
- YOLO12-L / YOLO26-L@640 已完成：`23.67 / 24.90 AP`，低于 DAHP-M 的 `26.11 AP`。

## 效率

当前 latency 均在单张 RTX 3090 上测试：batch 1、FP16、confidence 0.25、10 张 warmup 后测 50 张。更强版本应扩展到至少 200 张，并分别报告预处理、推理、后处理和显存。

## 当前完成状态

已完成：YOLO11/YOLO12/YOLO26 modern baselines、完整 YOLOv8l/P2 ladder、1920 曝光匹配控制、5 个 random-volume 种子、UAVDT 迁移和在线 two-arm 预测。

待最终回填：targeted-union 第 4--5 个种子、exact 1280 union/random controls、RT-DETR union 跨 detector family 结果。D-FINE 和 RT-DETRv2 是算力允许时建议补充的 modern DETR baselines。
