# DAHP: Regime-Dependent Rebalancing for UAV Object Detection

Official implementation of **"Regime-Dependent Rebalancing: A Data-Driven,
Non-Invasive Framework for Long-Tailed, Scale-Variant Object Detection in
UAV Imagery"**.

DAHP targets three coupled pathologies of UAV imagery with a single,
**label-only** profiler and **strictly non-invasive** training-time policies
(no architecture change, no loss change, no inference-time change):

1. **Long-tailed class distribution** (VisDrone head:tail ~ 45:1)
2. **Object-scale imbalance** (85.3% of instances < 32 px at the 640-px reference)
3. **Inter-class confusion** (23 class pairs with structural similarity > 0.85; head-anchored axis {van, truck})

## Key idea

A dataset profiler measures the three pathologies from labels alone and maps
them to a **resolution/backbone ladder** (R), **union oversampling** of tail
and confusion-axis classes (T+C), and optional **weighted-boxes fusion** (E).
A *regime-dependent rebalancing law* gates when sampling helps:

| Resolution | 640 | 960 | 1280 | 1600 | 1920 |
|---|---|---|---|---|---|
| dAP of union sampling | +0.21 | +3.15 | ~0 | +1.02 | +3.83 |
| Regime | unlearnable | under-fit | saturated | sweet spot | exposure-limited |

Rebalancing is positive-sum only in under-fitted / exposure-limited regimes;
in saturated regimes it is approximately zero-sum. This law was replicated on
UAVDT (union +0.69 AP overall, +1.69 tail) and is the core theoretical claim.

## Results (VisDrone val)

| Method | Input | AP (md100) | Params |
|---|---|---|---|
| YOLOv8m-P2 baseline | 1280 | 34.63 | 25.0M |
| V_L (vanilla large) | 1600 | 35.93 | 43.6M |
| V_L+P2 | 1600 | 37.59 | 42.8M |
| **DAHP-L (ours)** | **1600** | **38.16** | **42.8M** |
| RemDet-X (repro) | 640 | 29.90 | 74.1M |
| RemDet-X (compute-matched retrain) | 1600 | 29.7 | 74.1M |

Native maxDets=300 protocol: **DAHP-L 40.06 AP** (dual-seed 39.88 +/- 0.25);
WBF ensemble 39.61 (md100). DAHP-L uses **58% of RemDet-X parameters** and
runs at 24.5 FPS on one RTX 3090.

## Repository layout

```
dahp/        label-only profiler (three pathologies, regime signals)
scripts/     farm builders, evaluation, benchmarks, figure generation
configs/     example dataset configs
docs/        experiment protocol notes
paper/       manuscript LaTeX sources, figures, graphical abstract
```

## Installation

```bash
conda create -n dahp python=3.10 -y
conda activate dahp
pip install ultralytics pycocotools matplotlib numpy torch torchvision
```

Datasets: [VisDrone2019-DET](https://github.com/VisDrone/VisDrone-Dataset) and
[UAVDT](https://sites.google.com/site/daviddo0116/projects/uavdt) with YOLO
format labels.

## Quick start

### 1. Profile a dataset (labels only)

```bash
python - <<'PY'
from dahp.profiler import DatasetProfilerV2
prof = DatasetProfilerV2("configs/visdrone_example.yaml", img_size=1600)
profile = prof.profile()
PY
```

The profile reports tail classes, small/tiny-object ratios, suggested
resolution, and high-confusion pairs.

### 2. Build the union-oversample farm (non-invasive data rebalancing)

```bash
# VisDrone union recipe: tail classes 6,7,8 + confusion axis 1,2,4,5,7, x2 copies
python scripts/build_oversample_farm.py \
    --root data/VisDrone2019 \
    --out  data/VisDrone2019-dahp-union \
    --classes 1,2,4,5,6,7,8 --copies 2
```

Then train any stock detector (e.g. Ultralytics YOLOv8l-P2) on the farm yaml
- no trainer modification is required (symlink farm).

### 3. Evaluate with the paper protocol

```bash
python scripts/eval_dahp.py \
    --model runs/dahp_l_union/weights/best.pt \
    --img-dir data/VisDrone2019/VisDrone2019-DET-val/images \
    --imgsz 1600 --coco-maxdets 100 --tag DAHP-L
```

`eval_dahp.py` supports full / sliced / hybrid / ensemble (WBF) protocols and
both maxDets 100 and 300 evaluation.

### 4. Benchmark latency

```bash
python scripts/bench_fps.py \
    --val-dir data/VisDrone2019/VisDrone2019-DET-val/images \
    --runs dahp_l=runs/dahp_l_union/weights/best.pt:1600
```

## Documentation

- `docs/EXPERIMENTS.md` - full experimental protocol (fair-comparison rules,
  budgets, seeds, resolution ladders, negative results)
- `paper/` - manuscript source and figures

## Citation

```bibtex
@article{dahp_uav_detection,
  title   = {Regime-Dependent Rebalancing: A Data-Driven, Non-Invasive
             Framework for Long-Tailed, Scale-Variant Object Detection in
             UAV Imagery},
  author  = {AirAI-Lab},
  journal = {IEEE Transactions on Geoscience and Remote Sensing},
  year    = {2026},
  note    = {Under review}
}
```

## License

MIT License. See [LICENSE](LICENSE).
