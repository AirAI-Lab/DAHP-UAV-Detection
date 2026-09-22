# DAHP: Regime-Dependent Rebalancing for UAV Object Detection

[English](README.md) | [简体中文](README.zh-CN.md)

Code and reproducibility artifacts for **“Regime-Dependent Rebalancing for UAV Object
Detection: An Exposure-Aware Data-Centric Study”**.

DAHP is a label-only profiling mechanism followed by a bounded policy search.
It quantifies three coupled UAV-data pathologies---long-tailed classes, extreme
object-scale imbalance, and annotation-level structural confusion---and maps
them to a candidate resolution ladder, union oversampling, and optional fusion.
The rebalancing operation changes training exposure rather than the detector's
stock loss or inference module. Resolution, P2, and capacity choices are
explicitly disclosed and ablated.

## Exposure-aware regime principle

The same union-sampling policy has different effects as exposure headroom changes:

| Input | 640 | 960 | 1280 | 1600 | 1920 |
|---|---:|---:|---:|---:|---:|
| Same-epoch union gain (native AP) | +0.21 | +3.81 | approx. +0.05 | +0.78 | +3.83 |
| Exact md100 triplet | — | 28.10 / 31.77 / 31.92 | 34.63 / 34.72 / 35.12 | — | — |
| Interpretation | unlearnable | volume-dominated | volume-saturated | positive-sum window | exposure-limited |

At 1920 px, a 120-epoch exposure-matched base control reduces the apparent
+3.83 AP gain to +0.49 native AP / +0.42 md100 AP (+0.92 APs). Thus, resolution
alone is not the moderator; the operative question is whether additional exposure
can still be converted into useful learning.

## Bounded VisDrone-val result

All values use VisDrone validation under the disclosed protocol. This release
makes no official test-dev claim.

| Method | Input | AP md100 | Native AP | Params |
|---|---:|---:|---:|---:|
| YOLOv8m-P2 baseline | 1280 | 34.63 | 36.20 | 25.0M |
| YOLO11-L | 640 | 23.97 | — | 25.3M |
| YOLO12-L | 640 | 23.67 | — | 26.5M |
| YOLO26-L | 640 | 24.90 | — | 26.3M |
| D-FINE-M | 640 | 31.67 | — | 19.2M |
| RT-DETRv2-L | 640 | 29.47 | — | 42.7M |
| DAHP-M same-input control | 640 | 26.11 | — | 25.0M |
| Vanilla YOLOv8l | 1600 | 35.93 | 37.94 | 43.6M |
| YOLOv8l-P2 | 1600 | 37.59 | 39.04 | 42.8M |
| **DAHP-L single model** | **1600** | **38.16** | **40.06** | 42.8M |
| DAHP-L-E7 WBF ensemble | 1600 | 39.61 | — | 7 models |
| RemDet-X evaluated weights | 640 | 29.90 | — | 74.1M |

DAHP-M exceeds the reproduced modern YOLO baselines at 640 px but does not
exceed D-FINE-M or RT-DETRv2-L. DAHP-L is compared under its disclosed
1600-px/P2 policy, not as an architecture-only or same-input claim. A matched
single-seed RT-DETR-L wrapper probe is negative (15.51 vs. 7.61 md100 AP),
bounding the policy claim to the studied YOLO setup.

DAHP-L measures 38.0 ms end-to-end / 26.3 FPS on one exclusive desktop RTX 3090
with a 300-image stage-wise protocol; no edge-device claim is made.

## Quick start

```bash
conda env create -f environment.yml
conda activate dahp
```

Datasets: [VisDrone2019-DET](https://github.com/VisDrone/VisDrone-Dataset) and
[UAVDT](https://sites.google.com/site/daviddo0116/projects/uavdt), converted to
YOLO labels.

Profile labels only:

```bash
python - <<'PY'
from dahp.profiler import DatasetProfiler
profile = DatasetProfiler("configs/visdrone_example.yaml", img_size=1600).profile()
print([profile.class_names[c] for c in profile.tail_classes])
print([profile.class_names[c] for c in profile.confusion_axis])
PY
```

Audit threshold stability without training:

```bash
python scripts/profile_threshold_sensitivity.py \
  --label-dir data/VisDrone2019/VisDrone2019-DET-train/labels \
  --reference-size 1280 \
  --output results/eval/profile_threshold_sensitivity.json
```

Build a rebalanced training set:

```bash
python scripts/build_rebalanced_dataset.py \
  --root data/VisDrone2019 \
  --out data/VisDrone2019-dahp-union \
  --classes 4,5,6,7,8 --copies 2
```

Evaluate with the dual-maxDets protocol:

```bash
python scripts/eval_dahp.py \
  --model runs/dahp_l_union/weights/best.pt \
  --img-dir data/VisDrone2019/VisDrone2019-DET-val/images \
  --imgsz 1600 --coco-maxdets 100 --tag DAHP-L
```

Run the paper latency protocol:

```bash
python scripts/bench_fps.py \
  --val-dir data/VisDrone2019/VisDrone2019-DET-val/images \
  --device 0 --warmup 20 --measure 300 --require-exclusive \
  --tags baseline_v8mP2_1280,vanilla_v8l_1600,v8lP2_1600,dahpL_1600 \
  --output results/eval/fps_benchmark_300.json
```

## Documentation

- `docs/EXPERIMENT_PROTOCOL.md` / `.zh-CN.md`
- `docs/REPRODUCIBILITY.md` / `.zh-CN.md`
- `docs/FPS_PROTOCOL.md` / `.zh-CN.md`
- `docs/FACT_TABLE.md` / `.zh-CN.md`
- `results/eval/paper_results_public.json`

## Citation

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

MIT License. See [LICENSE](LICENSE).
