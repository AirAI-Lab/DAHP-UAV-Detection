# 实验协议

本文档定义论文使用的训练与评估协议。所有论文数值均来自
`results/eval/paper_results_public.json`；该文件的 `missing_sources=[]`。

## 范围

- **数据集：** VisDrone2019-DET 与 UAVDT。
- **主要诊断划分：** VisDrone validation（548 张）。
- **benchmark 声明范围：** 仅 validation 协议。未使用官方 VisDrone
  test-dev 真值，因此不做挑战服务器 SOTA 声明。
- **延迟硬件：** 一张 NVIDIA RTX 3090（24 GB）；训练所用 GPU 与协议在论文
  和脱敏结果文件中披露。
- **软件：** Python 3.10、PyTorch 2.5.1 + CUDA 12.1、Ultralytics 8.4.60。
  精确版本见 `environment.yml` 与 `requirements-lock.txt`。

## 公平比较规则

1. 只在已披露的输入尺寸、模型容量、训练日程、评估器和 checkpoint 选择
   规则内比较。
2. 外部方法若未在本研究中复现，则明确标注为文献值。
3. COCO `maxDets=100`（md100）与 native/Ultralytics `maxDets=300` 分开记录，
   不允许跨协议直接相减。
4. 在算力允许时匹配 epoch 与 batch 预算；所有偏差均披露，未匹配运行不进入
   严格消融。
5. 所有比较 arm 使用相同的 best-validation checkpoint 规则。
6. 多种子实验报告种子数、均值和标准差；对单种子方向性差异不作显著性表述。

## 训练日程

- **960 与 1280 px 精确控制组：** base/random-volume/union 每个 arm 单种子，
  triplet 内 batch 匹配，并使用统一 md100 evaluator。
- **1600 px random-volume 与 targeted-union 控制：** 各 5 个种子。
- **1920 px 曝光匹配：** 除 same-epoch 对比外，将 60-epoch union 与
  120-epoch base 对比，用于区分曝光与残余 rebalancing。
- **UAVDT 迁移：** 直接使用 VisDrone 导出的 label profiler 与 union 采样规则，
  不做数据集特定阈值调参。
- **现代通用 baseline：** YOLO11、YOLO12、YOLO26、D-FINE、RT-DETRv2 在
  640 px 下按论文披露的日程与 batch 复现。
- **跨家族边界探针：** RT-DETR-L wrapper、640 px、batch 2、100 epochs、
  单种子。这是负向边界观察，不是 detector-family independence 实验。

## 评估协议

`scripts/eval_dahp.py` 同时支持两种协议：

```bash
python scripts/eval_dahp.py \
  --model runs/dahp_l_union/weights/best.pt \
  --img-dir data/VisDrone2019/VisDrone2019-DET-val/images \
  --imgsz 1600 --coco-maxdets 100 --tag DAHP-L
```

使用 `--coco-maxdets 300` 得到 dense-scene/native 协议。脚本将不同协议的
指标分开保存；可释放的 checkpoint 来源记录在结果聚合文件中。

## 关键控制结果

| 分辨率 | 控制组 | 观察 |
|---:|---|---|
| 640 px | base vs. union | +0.21 AP；learnability 边界，tail 仍约 0.20 |
| 960 px | exact base/random/union | 28.10 / 31.77 / 31.92 md100 AP；volume +3.67，targeted +0.15 |
| 1280 px | exact base/random/union | 34.63 / 34.72 / 35.12 md100 AP；volume +0.09，targeted residual +0.40 |
| 1600 px | 每个采样 arm 5 seeds | R-only 36.55 ± 0.21，random 36.91 ± 0.29，targeted 37.18 ± 0.18 md100 AP |
| 1920 px | same-epoch 与曝光匹配 | same-epoch +3.83 native AP；匹配后残余 +0.49 native / +0.42 md100 AP |

30-epoch two-arm 分析是回顾性的。其 Pearson 相关与事后 2.5-AP 分界描述的是
已完成运行，不作为前瞻部署实验。

## Label-only 阈值审计

`scripts/profile_threshold_sensitivity.py` 检查邻近结构代理权重和图阈值是否会
改变所选策略：

```bash
python scripts/profile_threshold_sensitivity.py \
  --label-dir data/VisDrone2019/VisDrone2019-DET-train/labels \
  --reference-size 1280 \
  --output results/eval/profile_threshold_sensitivity.json
```

审计覆盖 lambda = 0.4、0.5、0.6、0.7 与阈值 0.80、0.85、0.90。它仅审计
决策集合；替代采样集未训练，因此不声明 AP 敏感性。

## 延迟与显存协议

论文使用 `scripts/bench_fps.py`：20 张 warm-up、300 张测量图、batch 1、FP16、
每张图后 CUDA 同步，并在独占桌面级 RTX 3090 上执行。预处理、推理、后处理、
端到端时间、active/reserved CUDA memory 与主机负载来源分别记录。RTX 3090
不被描述为 edge 设备。
