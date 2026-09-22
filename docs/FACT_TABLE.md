# Fact Table

This table records the facts and protocol boundaries used by the manuscript.
Numerical entries are traceable to `results/eval/paper_results_public.json`.

## Data and profile

| Item | VisDrone2019-DET | UAVDT |
|---|---|---|
| Train images / instances | 6,471 / 343,204 | profiler input as disclosed in the paper |
| Evaluation | validation, 548 images | converted validation split |
| Head-to-tail ratio | 44.6:1 | 30.7:1 |
| Small instances at reference | 85.3% < 32 px at 640 reference | 74.8% < 32 px at 640 reference |
| Tail classes | tricycle, awning-tricycle, bus | truck, bus |
| Structural confusion axis | van, truck | van |
| Confusion graph | 23 pairs with kappa > 0.85 | car-van kappa = 0.935 |

The scale statistic is computed in a square reference space from normalized
label extents; it is a policy statistic, not a sensor-calibrated length.

## Main VisDrone-val results

| Configuration | Input | md100 AP | Native AP | Parameters |
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
| DAHP-L single model | 1600 | 38.16 | 40.06 | 42.8M |
| DAHP-L-E7 WBF ensemble | 1600 | 39.61 | — | 7 models |
| RemDet-X evaluated weights | 640 | 29.90 | — | 74.1M |

Interpretation boundaries: DAHP-M does not outperform D-FINE-M or RT-DETRv2-L
at 640 px. DAHP-L is a disclosed 1600-px/P2 policy, not an architecture-only or
same-input claim. Literature rows are context and are not mixed with reproduced
subtractions.

## Mechanism controls

| Control | Result |
|---|---|
| Exact 960 base/random/union | 28.1009 / 31.7702 / 31.9239 md100 AP |
| Exact 1280 base/random/union | 34.6296 / 34.7233 / 35.1223 md100 AP |
| 1600 R-only / random / targeted | 36.55 ± 0.21 / 36.91 ± 0.29 / 37.18 ± 0.18 md100 AP, n=3/5/5 |
| 1920 union@60 / base@120 | native 39.50 / 39.01; md100 37.93 / 37.51 |
| Exposure-matched residual | +0.49 native AP, +0.42 md100 AP, +0.92 APs |
| Retrospective 30-epoch probe | Pearson r=0.983; post-hoc 2.5-AP cut separates 5/5 completed cases |
| UAVDT base / frequency / union | 37.86 / 37.80 / 38.55 AP; tail 32.05 / 31.49 / 33.73 |
| Label-only threshold grid | VisDrone tail set invariant over 12 settings; van invariant; local axis {van,truck} for lambda 0.6–0.7 at tau 0.85; UAVDT policy invariant |

The early-signal analysis is retrospective and is not a prospective policy
simulation.

## Negative and boundary results

- Seven feature-module generations in matched trainings change AP by −0.7 to
  +0.1 while increasing validation DFL.
- Direct tiled inference on full-image-trained models loses 2.3–2.6 AP.
- The matched RT-DETR-L wrapper probe is negative: base 15.5101 md100 AP versus
  union 7.6136 md100 AP.
- The RT-DETR probe is single-seed, batch-2, and wrapper-specific; it does not
  support detector-family independence.

## Efficiency

DAHP-L measures 38.0215 ms end-to-end and 26.3009 FPS on one exclusive desktop
RTX 3090 using 300 measured images. Stage timings and memory are reported in
`docs/FPS_PROTOCOL.md`. No edge-device claim is made.

## Environment

Python 3.10.20, PyTorch 2.5.1+cu121, torchvision 0.20.1+cu121, CUDA 12.1,
cuDNN 90100, Ultralytics 8.4.60. The full lock is in `environment.yml`.
