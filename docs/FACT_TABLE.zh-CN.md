# DAHP 论文事实表

> 目标：防止叙事漂移。论文中的每个 claim 都必须能追溯到本表、评估 JSON 或已核实文献。标记为 **pending** 的内容不得写成最终结论。

## 1. 研究对象与数据集

| 项目 | 固定事实 | 说明 / 证据状态 |
|---|---|---|
| 主数据集 | VisDrone2019-DET | train 6,471 张；val 548 张；10 类 |
| 主验证集实例数 | 38,759 个框 | 用于密度与画像统计 |
| 迁移数据集 | UAVDT | 同一 label-only profiler，不做数据集级调参 |
| 评估 split | VisDrone val | test-dev 公开 GT 不可得，因此不作为最终 benchmark SOTA claim |
| Profiler 输入 | 仅标签 | 不解码图像、不计算梯度、不依赖模型推理或预测混淆矩阵 |
| Profiler 输出 | 长尾、尺度、结构混淆统计 | 映射到分辨率/backbone 与采样策略 |

### VisDrone 画像

| 病理 | 论文值 | 状态 |
|---|---:|---|
| head-tail 比 | 45:1 | 已在训练标签上验证 |
| 640 参考分辨率下 <32 px 实例 | 85.3% | 已验证 |
| head-anchored confusion axis | van, truck | 由 structural-similarity graph 得到 |
| structural similarity >0.85 的类别对 | 23 | 已验证 |
| confusion score | 0.6 aspect-ratio overlap + 0.4 scale overlap | 论文、代码和验证脚本一致 |

### UAVDT 画像

| 病理 | 数值 | 状态 |
|---|---:|---|
| head-tail 比 | 30.7:1 | 已验证 |
| 640 参考下小目标比例 | 74.8% | 已验证 |
| 最强 confusion pair | car--van, 0.935 | 已验证 |
| policy axis | van；union 集合为 truck/bus/van | zero-shot transfer |

## 2. 硬件与训练协议

| 项目 | 事实 |
|---|---|
| GPU | NVIDIA RTX 3090, 24 GB |
| 主 YOLO 环境 | Ultralytics 8.4.60, PyTorch 2.5.1 + CUDA 12.1 |
| 常规 schedule | 除特别声明外 100 epochs |
| 分辨率阶梯 | 640 / 960 / 1280 / 1600 / 1920 |
| 640 baseline batch | 8 |
| 1600 YOLOv8m-P2 controls | batch 2 |
| RT-DETR-L baseline | 640 px, batch 4, 100 epochs |
| RT-DETR-L batch 匹配对照 | 640 px, batch 2, 100 epochs；运行中 |
| 960 px batch 匹配 base/union | 960 px, batch 2, 60 epochs；已完成 |
| 960 px exact random-volume control | 12,276 张图曝光，batch 2，60 epochs；运行中 |
| D-FINE-M baseline | 640 px, total batch 8, 100 epochs；修复 evaluator 后从 epoch 50 续跑 |
| D-FINE 验证 batch | 2 | 共享 GPU6 的显存控制；不改变训练曝光 |
| 种子策略 | 报告 n、均值和标准差；样本不足不使用显著性表述 |
| 服务器恢复 | checkpoint resume + reboot-safe queue scripts |

计算受限的 RemDet retrain 和较短探索性运行均在论文或负结果附录中披露。

## 3. 评估协议

| 协议 | 含义 | 用途 |
|---|---|---|
| md100 | COCO 风格 AP, maxDets=100 | 主表与归因控制 |
| native/md300 | Ultralytics 风格密集协议, maxDets=300 | native training-selection 与 regime matrix |
| APs/APm/APl | COCO 面积区间 | 小目标证据 |
| best checkpoint | 声明 schedule 内最高 val mAP | 主结果 |
| final checkpoint | 保留在日志中，不替代 best checkpoint | 审计 |

规则：

1. 不得在一个减法中混用 md100 与 native。
2. 明确区分 reproduced、official weights reproduction 和 literature-only。
3. 文献值只是上下文，不是同协议证据。
4. 主表括号中的数值表示 secondary native protocol。

## 4. 已完成关键结果

### VisDrone 主结果

| 配置 | 输入 | 协议 | AP | 说明 |
|---|---:|---:|---:|---|
| DAHP-M full | 640 | md100 | 26.11 | 同输入 modern baseline 对比 |
| YOLO26-L | 640 | md100 | 24.90 | 当前最强 reproduced modern YOLO baseline |
| YOLO12-L | 640 | md100 | 23.67 | 已完成 |
| YOLO11-L | 640 | md100 | 23.97 | 已完成 |
| Baseline YOLOv8m-P2 | 1280 | md100 | 34.63 | 主 baseline |
| DAHP-L | 1600 | md100 | 38.16 | 单模型 |
| DAHP-L | 1600 | native | 40.06 | secondary protocol |
| DAHP-L E7 | 1600 | md100 | 39.61 | ensemble，单独报告 |

### 同 detector P2 ladder，native/md300

| Detector | 640 | 1280 | 1600 |
|---|---:|---:|---:|
| YOLOv8l vanilla | 23.21 | 33.76 | 37.94 |
| YOLOv8l-P2 | 27.21 | 37.96 | 39.04 |
| P2 gain | +4.0 | +4.2 | +1.1 |

### 1280 px exact regime controls

三条 arm 均使用同一 external COCO evaluator、1280 px 输入、v8m-P2、
100 epochs、每 arm 一个 seed。不得与 legacy native/md300 law-matrix 单元格直接相减。

| Arm | md100 AP | md100 AP50 | md100 APs | native AP | Tail mean |
|---|---:|---:|---:|---:|---:|
| Base | 34.6296 | 54.8244 | 26.2765 | 34.6859 | 0.3202 |
| Random volume | 34.7233 | 55.0512 | 26.7730 | 34.7770 | 0.3168 |
| Targeted union | 35.1223 | 55.4333 | 26.9803 | 35.1772 | 0.3221 |

md100 分解：base→random 的 volume效应为 `+0.0937 AP`；random→union 的
targeted residual 为 `+0.3990 AP`。因此该 regime 是 **volume-saturated**，
不是严格 zero-sum。

### 960 px exact batch 匹配对照

两条 arm 均为 960 px 输入、v8m-P2、batch 2、60 epochs、seed 0。

| Arm | md100 AP | md100 AP50 | md100 APs | native AP | Tail mean |
|---|---:|---:|---:|---:|---:|
| Base | 28.1009 | 45.4306 | 19.4636 | 28.1722 | 0.2084 |
| Targeted union | 31.9239 | 50.9051 | 23.6240 | 31.9794 | 0.2561 |

匹配后的 union 效应为 **+3.8231 md100 AP / +3.8072 native AP**；
APs 提升 `+4.1603` 点，tail mean 提升 `+4.7704` 点。严格机制 claim
应使用该结果，替代旧 batch6 base vs batch2 union 的直接相减。

### D-FINE COCO 类别映射修正

前 50 个 log 中的 D-FINE COCO AP 不能用于论文。Detector 输出的是
0-based VisDrone 类别，而 COCO GT 使用 category ID 1--10；上游 evaluator
未做数据集特定 `label2category` 映射。训练权重和 loss 不受影响。
checkpoint 49 的 batch-8 sanity check 结果：

| Evaluator 状态 | COCO AP | AP50 | APs |
|---|---:|---:|---:|
| 类别映射修正前 | 2.8 | 4.9 | 2.2 |
| `label2category` 修正后 | 30.2 | 49.1 | 20.2 |

训练已使用修正后的 COCO evaluator 从 epoch 50 恢复。论文最终指标只能
来自修正后的评估。

### 1600 px 曝光归因，md100

| Arm | n | AP | Tail mean |
|---|---:|---:|---:|
| R only | 3 | 36.55 ± 0.21 | 0.339 |
| Random volume control | 5 | 36.91 ± 0.29 | 0.341 |
| Targeted union | 3 completed | 37.09 ± 0.16 | 0.346 |

当前解释：volume 贡献 `+0.36 AP`，targeted reallocation 贡献 `+0.18 AP`。两个额外 targeted seeds 完成后必须替换该 3-seed 统计。

### 1920 px 曝光匹配控制

| Arm | Schedule | native AP | md100 AP | APs |
|---|---:|---:|---:|---:|
| Base | 60 ep | 35.67 | 不作为匹配比较 | — |
| Union | 60 ep | 39.50 | 37.93 | 30.46 |
| Base | 120 ep | 39.01 | 37.51 | 29.54 |
| Matched residual | union60 - base120 | +0.49 | +0.42 | +0.92 |

结论：same-epoch `+3.83 AP` 不能单独归因于 targeted sampling；大部分来自 exposure。

### Online two-arm prediction

| 诊断量 | 结果 |
|---|---:|
| probe epoch | 30 |
| 与最终 gain 的 Pearson correlation | 0.983 |
| positive/saturated separation | 5/5 |
| threshold | probe gap >2.5 AP |
| negative control | single-arm epoch-gain statistic 无法区分 regime |

### UAVDT transfer

| Arm | AP | Tail |
|---|---:|---:|
| Base | 37.86 | 32.05 |
| Frequency-only | 37.80 | 31.49 |
| Union | 38.55 | 33.73 |

## 5. Pending 事实

| Pending 项 | 当前用途 | 最终 claim 前必须完成 |
|---|---|---|
| Targeted union seeds 4--5 | 将 targeted arm 扩展到 n=5 | 100 epochs + md100 评估 |
| Exact 960 random-volume control | 替代 legacy 77/23 分解 | 60 epochs + md100/native 评估 |
| RT-DETR batch-2 base 与 union arm | detector-family independence | 收敛训练并统一评估 |
| D-FINE / RT-DETRv2 baselines | reviewer 相关 modern DETR comparison | 完成披露预算训练并适配 evaluator 输出 |
| VisDrone test-dev | 外部 benchmark claim | challenge-server 评估；否则保留 val limitation |
| Expanded FPS protocol | 更强效率证据 | 预处理/推理/后处理分解，至少 200 张 |

## 6. Claim 用语规则

| 不建议 | 建议 |
|---|---|
| 无协议条件的 state of the art by X AP | strongest reproduced comparator under our protocol |
| 整个系统 zero architecture change | rebalancing policy 本身不引入结构修改 |
| rebalancing law | exposure-aware regime-dependent rebalancing principle |
| 1280 是 zero-sum | 1280 是 volume-saturated；exact targeted residual 为 random 之上 +0.40 md100 |
| union 在 1920 获得 +3.83 AP | same-epoch gain +3.83；曝光匹配 residual +0.42 md100 |
| edge real-time | desktop RTX 3090 real-time |
| n<5 时 statistically significant | 报告 n、mean、std 和 paired differences；合适时使用 CI |
