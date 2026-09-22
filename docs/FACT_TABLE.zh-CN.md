# 事实表

本表记录论文使用的事实与协议边界。数值条目可追溯到
`results/eval/paper_results_public.json`。

## 数据与画像

| 项目 | VisDrone2019-DET | UAVDT |
|---|---|---|
| 训练图像 / 实例 | 6,471 / 343,204 | 论文披露的 profiler 输入 |
| 评估 | validation，548 张 | 转换后的 validation split |
| Head-to-tail 比 | 44.6:1 | 30.7:1 |
| 参考尺度下小目标 | 640 参考下 85.3% < 32 px | 640 参考下 74.8% < 32 px |
| Tail classes | tricycle、awning-tricycle、bus | truck、bus |
| 结构混淆轴 | van、truck | van |
| Confusion graph | 23 对 kappa > 0.85 | car-van kappa = 0.935 |

尺度统计在方形参考空间中由归一化标注尺度计算；它是策略统计，不是传感器标定
长度。

## VisDrone-val 主结果

| 配置 | 输入 | md100 AP | Native AP | 参数 |
|---|---:|---:|---:|---:|
| YOLOv8m-P2 baseline | 1280 | 34.63 | 36.20 | 25.0M |
| YOLO11-L | 640 | 23.97 | — | 25.3M |
| YOLO12-L | 640 | 23.67 | — | 26.5M |
| YOLO26-L | 640 | 24.90 | — | 26.3M |
| D-FINE-M | 640 | 31.67 | — | 19.2M |
| RT-DETRv2-L | 640 | 29.47 | — | 42.7M |
| DAHP-M 同输入控制 | 640 | 26.11 | — | 25.0M |
| Vanilla YOLOv8l | 1600 | 35.93 | 37.94 | 43.6M |
| YOLOv8l-P2 | 1600 | 37.59 | 39.04 | 42.8M |
| DAHP-L 单模型 | 1600 | 38.16 | 40.06 | 42.8M |
| DAHP-L-E7 WBF ensemble | 1600 | 39.61 | — | 7 models |
| RemDet-X 评估权重 | 640 | 29.90 | — | 74.1M |

解释边界：DAHP-M 在 640 px 未超过 D-FINE-M 或 RT-DETRv2-L。DAHP-L 是披露的
1600-px/P2 策略，不是 architecture-only 或同输入声明。文献值只作为背景，不与
复现值混合相减。

## 机制控制

| 控制 | 结果 |
|---|---|
| Exact 960 base/random/union | 28.1009 / 31.7702 / 31.9239 md100 AP |
| Exact 1280 base/random/union | 34.6296 / 34.7233 / 35.1223 md100 AP |
| 1600 R-only / random / targeted | 36.55 ± 0.21 / 36.91 ± 0.29 / 37.18 ± 0.18 md100 AP，n=3/5/5 |
| 1920 union@60 / base@120 | native 39.50 / 39.01；md100 37.93 / 37.51 |
| 曝光匹配残余 | +0.49 native AP、+0.42 md100 AP、+0.92 APs |
| 回顾性 30-epoch probe | Pearson r=0.983；事后 2.5-AP 分界区分 5/5 已完成案例 |
| UAVDT base / frequency / union | 37.86 / 37.80 / 38.55 AP；tail 32.05 / 31.49 / 33.73 |
| Label-only 阈值网格 | VisDrone tail set 在 12 个设置下不变；van 不变；lambda 0.6–0.7 且 tau 0.85 时局部轴为 {van,truck}；UAVDT 策略不变 |

Early-signal 分析是回顾性的，不是前瞻策略仿真。

## 负结果与边界

- 匹配训练中的七代 feature-module 使 AP 变化为 −0.7 到 +0.1，同时提高
  validation DFL。
- full-image 训练模型直接 tiled inference 损失 2.3–2.6 AP。
- matched RT-DETR-L wrapper probe 为负：base 15.5101 md100 AP，union
  7.6136 md100 AP。
- RT-DETR probe 是单种子、batch-2、wrapper-specific；不支持
  detector-family independence。

## 效率

DAHP-L 在独占桌面级 RTX 3090 上用 300 张测量图得到 38.0215 ms end-to-end /
26.3009 FPS。阶段时间与显存见 `docs/FPS_PROTOCOL.md`。不做 edge-device 声明。

## 环境

Python 3.10.20、PyTorch 2.5.1+cu121、torchvision 0.20.1+cu121、CUDA 12.1、
cuDNN 90100、Ultralytics 8.4.60。完整锁定见 `environment.yml`。
