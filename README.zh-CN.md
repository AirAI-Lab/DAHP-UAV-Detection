# DAHP：面向 UAV 目标检测的 Regime-Dependent Rebalancing

[English](README.md) | [简体中文](README.zh-CN.md)

**《Regime-Dependent Rebalancing for UAV Object Detection: An Exposure-Aware
Data-Centric Study》** 的代码与可复现性工件。

DAHP 是“label-only 画像 + 有界策略搜索”机制。它量化 UAV 数据中的三个耦合
病理---类别长尾、极端尺度不均衡、标注级结构混淆---并映射到候选分辨率阶梯、
union oversampling 与可选 fusion。Rebalancing 改变训练曝光，不改变检测器的
原生损失或推理模块；分辨率、P2 与容量选择被明确披露并单独消融。

## Exposure-aware regime principle

同一个 union-sampling 策略会随 exposure headroom 变化表现出不同效果：

| 输入 | 640 | 960 | 1280 | 1600 | 1920 |
|---|---:|---:|---:|---:|---:|
| Same-epoch union gain（native AP） | +0.21 | +3.81 | 约 +0.05 | +0.78 | +3.83 |
| Exact md100 triplet | — | 28.10 / 31.77 / 31.92 | 34.63 / 34.72 / 35.12 | — | — |
| 解释 | unlearnable | volume-dominated | volume-saturated | positive-sum window | exposure-limited |

在 1920 px，120-epoch 曝光匹配 base 控制将表观 +3.83 AP 增益降为
+0.49 native AP / +0.42 md100 AP（APs +0.92）。因此，调节变量不是分辨率本身，
而是额外曝光是否仍能转化为有效学习。

## 有边界的 VisDrone-val 结果

以下结果均使用 VisDrone validation 与披露协议；本仓库不做官方 test-dev 声明。

| 方法 | 输入 | AP md100 | Native AP | 参数 |
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
| **DAHP-L 单模型** | **1600** | **38.16** | **40.06** | 42.8M |
| DAHP-L-E7 WBF ensemble | 1600 | 39.61 | — | 7 models |
| RemDet-X 评估权重 | 640 | 29.90 | — | 74.1M |

DAHP-M 在 640 px 超过复现的现代 YOLO baseline，但未超过 D-FINE-M 或
RT-DETRv2-L。DAHP-L 的比较基于披露的 1600-px/P2 策略，不是 architecture-only
或同输入声明。matched 单种子 RT-DETR-L wrapper probe 为负向结果
（15.51 vs 7.61 md100 AP），因此策略结论限于所研究的 YOLO 设置。

DAHP-L 在独占桌面级 RTX 3090 上以 300 张图 stage-wise 协议测得
38.0 ms end-to-end / 26.3 FPS；不做 edge-device 声明。

## 快速开始

```bash
conda env create -f environment.yml
conda activate dahp
```

数据集：[VisDrone2019-DET](https://github.com/VisDrone/VisDrone-Dataset) 与
[UAVDT](https://sites.google.com/site/daviddo0116/projects/uavdt)，需转换为
YOLO 标签格式。

仅从标签画像：

```bash
python - <<'PY'
from dahp.profiler import DatasetProfiler
profile = DatasetProfiler("configs/visdrone_example.yaml", img_size=1600).profile()
print([profile.class_names[c] for c in profile.tail_classes])
print([profile.class_names[c] for c in profile.confusion_axis])
PY
```

无需训练即可审计阈值稳定性：

```bash
python scripts/profile_threshold_sensitivity.py \
  --label-dir data/VisDrone2019/VisDrone2019-DET-train/labels \
  --reference-size 1280 \
  --output results/eval/profile_threshold_sensitivity.json
```

构建 rebalanced 训练集：

```bash
python scripts/build_rebalanced_dataset.py \
  --root data/VisDrone2019 \
  --out data/VisDrone2019-dahp-union \
  --classes 4,5,6,7,8 --copies 2
```

使用双 maxDets 协议评估：

```bash
python scripts/eval_dahp.py \
  --model runs/dahp_l_union/weights/best.pt \
  --img-dir data/VisDrone2019/VisDrone2019-DET-val/images \
  --imgsz 1600 --coco-maxdets 100 --tag DAHP-L
```

运行论文延迟协议：

```bash
python scripts/bench_fps.py \
  --val-dir data/VisDrone2019/VisDrone2019-DET-val/images \
  --device 0 --warmup 20 --measure 300 --require-exclusive \
  --tags baseline_v8mP2_1280,vanilla_v8l_1600,v8lP2_1600,dahpL_1600 \
  --output results/eval/fps_benchmark_300.json
```

## 文档

- `docs/EXPERIMENT_PROTOCOL.md` / `.zh-CN.md`
- `docs/REPRODUCIBILITY.md` / `.zh-CN.md`
- `docs/FPS_PROTOCOL.md` / `.zh-CN.md`
- `docs/FACT_TABLE.md` / `.zh-CN.md`
- `results/eval/paper_results_public.json`

## 引用

```bibtex
@article{dahp_uav_detection,
  title   = {Regime-Dependent Rebalancing for UAV Object Detection:
             An Exposure-Aware Data-Centric Study},
  author  = {Wen, Nu and Zhou, Ying and Chen, Yebin},
  journal = {IEEE Transactions on Geoscience and Remote Sensing},
  year    = {2026},
  note    = {Under review}
}
```

## License

MIT License。见 [LICENSE](LICENSE)。
