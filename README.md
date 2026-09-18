# DAHP: Regime-Dependent Rebalancing for UAV Object Detection

[English](README.md) | [简体中文](README.zh-CN.md)

Official implementation of **"Regime-Dependent Rebalancing: An Exposure-Aware
Data-Driven Framework for Long-Tailed UAV Object Detection"**.

DAHP targets three coupled pathologies of UAV imagery with a single,
**label-only** profiler and **strictly non-invasive** training-time policies
(the sampling policy itself adds no architecture, loss, or inference-time change):

1. **Long-tailed class distribution** (VisDrone head:tail ~ 45:1)
2. **Object-scale imbalance** (85.3% of instances < 32 px at the 640-px reference)
3. **Inter-class confusion** (23 class pairs with structural similarity > 0.85; head-anchored axis {van, truck})

## Key idea

A dataset profiler measures the three pathologies from labels alone and maps
them to a **resolution/backbone ladder** (R), **union oversampling** of tail
and confusion-axis classes (T+C), and optional **weighted-boxes fusion** (E).
An *exposure-aware regime-dependent rebalancing principle* gates when sampling helps:

| Resolution | 640 | 960 | 1280 | 1600 | 1920 |
|---|---|---|---|---|---|
| Same-epoch union dAP | +0.21 | +3.15 | ~0 | +0.78 | +3.83 |
| Exposure-matched residual | — | — | pending | — | +0.49 native / +0.42 md100 |
| Regime | unlearnable | under-fit | saturated | sweet spot | exposure-limited |

Rebalancing is positive-sum only when learnability and exposure headroom permit;
in saturated regimes it is approximately zero-sum. The 1920-px same-epoch gain
is mostly an exposure effect: after a 120-epoch exposure-matched control, the
residual is +0.49 native / +0.42 md100 AP and +0.92 APs. The same profiler
recipe transfers to UAVDT (+0.69 AP overall, +1.69 tail).

## Results (VisDrone val)

| Method | Input | AP (md100) | Params |
|---|---|---|---|
| YOLOv8m-P2 baseline | 1280 | 34.63 | 25.0M |
| YOLO12-L | 640 | 23.67 | 26.5M |
| YOLO26-L | 640 | 24.90 | 26.3M |
| DAHP-M | 640 | 26.11 | 25.0M |
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
docs/        bilingual experiment, fact, evidence, and process documents
skills/      reusable evidence workflow
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

Bilingual pairs are maintained as `*.md` and `*.zh-CN.md`.

- `docs/FACT_TABLE.md` - objective manuscript facts and pending items
- `docs/REVISION_EVIDENCE_MATRIX.md` - claim-to-evidence audit and reviewer-risk matrix
- `docs/claim_evidence.csv` - machine-readable claim/evidence/status index
- `docs/PAPER_PROCESS_PLAYBOOK.md` - reusable paper-writing and experiment-audit process
- `docs/PAPER_PROCESS_PLAYBOOK.zh-CN.md` - Chinese reusable paper-process tutorial
- `skills/paper-evidence-workflow/` - bilingual evidence-first manuscript workflow skill
- `docs/EXPERIMENTS.md` - experimental protocol and fair-comparison rules
- `paper/` - manuscript source and figures

## Citation

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
