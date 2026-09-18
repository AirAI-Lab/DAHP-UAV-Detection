# DAHP: 面向 UAV 目标检测的 Regime-Dependent Rebalancing

论文 **“Regime-Dependent Rebalancing: An Exposure-Aware Data-Driven Framework for Long-Tailed UAV Object Detection”** 的官方实现。

DAHP 面向 UAV 图像中的三个耦合病理，使用 **label-only** profiler 和**非侵入式**训练期策略：

1. **长尾类别分布**：VisDrone head-tail 约 45:1。
2. **目标尺度失衡**：640 参考分辨率下 85.3% 实例小于 32 px。
3. **类间结构混淆**：23 个类别对的 structural similarity >0.85；head-anchored axis 为 `{van, truck}`。

## 核心思想

Dataset profiler 仅从标签度量三类病理，并映射为：

- resolution/backbone ladder；
- tail + confusion-axis union oversampling；
- optional weighted-boxes fusion。

当前核心理论为 **exposure-aware regime-dependent rebalancing principle**：

| 分辨率 | 640 | 960 | 1280 | 1600 | 1920 |
|---|---:|---:|---:|---:|---:|
| same-epoch union dAP | +0.21 | +3.15 | ~0 | +0.78 | +3.83 |
| exposure-matched residual | — | — | pending | — | +0.49 native / +0.42 md100 |
| regime | unlearnable | under-fit | saturated | intermediate | exposure-limited |

1920 px 的 same-epoch 增益主要由曝光量解释；曝光匹配后 residual 为 `+0.49 native / +0.42 md100 AP`，且 APs 提升 `+0.92`。同一策略迁移到 UAVDT：整体 `+0.69 AP`，tail `+1.69 AP`。

## VisDrone val 结果

| 方法 | 输入 | AP (md100) | Params |
|---|---:|---:|---:|
| YOLOv8m-P2 baseline | 1280 | 34.63 | 25.0M |
| YOLO12-L | 640 | 23.67 | 26.5M |
| YOLO26-L | 640 | 24.90 | 26.3M |
| DAHP-M | 640 | 26.11 | 25.0M |
| DAHP-L | 1600 | **38.16** | 42.8M |
| RemDet-X (repro) | 640 | 29.90 | 74.1M |
| RemDet-X (compute-matched retrain) | 1600 | 29.7 | 74.1M |

Native `maxDets=300`：DAHP-L `40.06 AP`；WBF ensemble md100 `39.61 AP`。DAHP-L 使用 RemDet-X 约 58% 参数，在单张 RTX 3090、1600 px 下约 24.5 FPS。

## 仓库结构

```text
dahp/        label-only profiler
scripts/     farm builders, evaluation, benchmarks, figures
configs/     example dataset configs
docs/        bilingual experiment, fact, evidence, and process documents
skills/      reusable paper-evidence workflow
paper/       LaTeX source, figures, graphical abstract
```

## 安装

```bash
conda create -n dahp python=3.10 -y
conda activate dahp
pip install ultralytics pycocotools matplotlib numpy torch torchvision
```

数据集：

- [VisDrone2019-DET](https://github.com/VisDrone/VisDrone-Dataset)
- [UAVDT](https://sites.google.com/site/daviddo0116/projects/uavdt)，转换为 YOLO 标签格式。

## 快速开始

### 1. Profile 数据集（仅标签）

```bash
python - <<'PY'
from dahp.profiler import DatasetProfilerV2
profiler = DatasetProfilerV2("configs/visdrone_example.yaml", img_size=1600)
profile = profiler.profile()
PY
```

输出 tail classes、small/tiny ratios、建议分辨率和高混淆类别对。

### 2. 构建 union-oversample farm

```bash
python scripts/build_oversample_farm.py \
  --root data/VisDrone2019 \
  --out  data/VisDrone2019-dahp-union \
  --classes 1,2,4,5,6,7,8 --copies 2
```

随后用任意 stock detector 训练该 farm YAML；symlink farm 不需要修改 trainer。

### 3. 按论文协议评估

```bash
python scripts/eval_dahp.py \
  --model runs/dahp_l_union/weights/best.pt \
  --img-dir data/VisDrone2019/VisDrone2019-DET-val/images \
  --imgsz 1600 --coco-maxdets 100 --tag DAHP-L
```

支持 full / sliced / hybrid / ensemble，并同时支持 `maxDets=100/300`。

### 4. Latency benchmark

```bash
python scripts/bench_fps.py \
  --val-dir data/VisDrone2019/VisDrone2019-DET-val/images \
  --runs dahp_l=runs/dahp_l_union/weights/best.pt:1600
```

## 文档

- `docs/FACT_TABLE.md` / `docs/FACT_TABLE.zh-CN.md` — 客观事实表
- `docs/REVISION_EVIDENCE_MATRIX.md` / `.zh-CN.md` — claim-evidence 审计
- `docs/PAPER_PROCESS_PLAYBOOK.md` / `.zh-CN.md` — 论文过程手册
- `docs/EXPERIMENTS.md` / `.zh-CN.md` — 实验协议
- `docs/claim_evidence.csv` — machine-readable claim index
- `skills/paper-evidence-workflow/` — reusable evidence workflow
- `paper/` — 论文源码与图表

## 引用

```bibtex
@article{dahp_uav_detection,
  title   = {Regime-Dependent Rebalancing: An Exposure-Aware Data-Driven
             Framework for Long-Tailed UAV Object Detection},
  author  = {AirAI-Lab},
  journal = {IEEE Transactions on Geoscience and Remote Sensing},
  year    = {2026},
  note    = {Under review}
}
```

## License

MIT License. See [LICENSE](LICENSE).
