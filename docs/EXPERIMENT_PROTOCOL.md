# Experiment Protocol

This document defines the evaluation and training protocol used by the paper.
All numerical tables are derived from `results/eval/paper_results_public.json`;
the file reports `missing_sources=[]`.

## Scope

- **Datasets:** VisDrone2019-DET and UAVDT.
- **Primary diagnostic split:** VisDrone validation (548 images).
- **Benchmark claim:** validation protocol only. No official VisDrone test-dev
  ground truth is used, so no challenge-server state-of-the-art claim is made.
- **Hardware:** one NVIDIA RTX 3090 (24 GB) for the reported latency benchmark;
  training used the GPUs disclosed in the manuscript and sanitized result file.
- **Software:** Python 3.10, PyTorch 2.5.1 + CUDA 12.1, Ultralytics 8.4.60.
  The exact lock is provided in `environment.yml` and `requirements-lock.txt`.

## Fair-comparison rules

1. Compare only within a disclosed input size, capacity, schedule, evaluator,
   and checkpoint-selection protocol.
2. Label external numbers as literature values unless reproduced in this study.
3. Keep COCO `maxDets=100` (md100) and native/Ultralytics `maxDets=300` values
   in separate fields. Never subtract values across protocols.
4. Match epochs and batch budget where computationally possible; disclose all
   deviations and avoid using unmatched runs in strict ablations.
5. Select checkpoints by the same best-validation rule in all compared arms.
6. Report seed count, mean, and standard deviation when multiple seeds exist;
   do not attach significance language to directional single-seed differences.

## Training schedule

- **Exact 960-px and 1280-px controls:** one seed per base/random-volume/union
  arm, batch-matched within each triplet, and evaluated with one unified md100
  evaluator.
- **1600-px random-volume and targeted-union controls:** five seeds each.
- **1920-px exposure matching:** compare union at 60 epochs with base at 120
  epochs, in addition to the same-epoch comparison, to separate exposure from
  residual rebalancing.
- **UAVDT transfer:** the VisDrone-derived label profiler and union-sampling
  rule are applied without dataset-specific threshold tuning.
- **Modern general-purpose baselines:** YOLO11, YOLO12, YOLO26, D-FINE, and
  RT-DETRv2 are reproduced at 640 px under the schedules and batch sizes
  disclosed in the manuscript.
- **Cross-family boundary probe:** a single-seed RT-DETR-L wrapper comparison
  at 640 px, batch 2, 100 epochs. It is a negative boundary observation, not a
  detector-family-independence experiment.

## Evaluation protocol

`scripts/eval_dahp.py` performs both supported protocols:

```bash
python scripts/eval_dahp.py \
  --model runs/dahp_l_union/weights/best.pt \
  --img-dir data/VisDrone2019/VisDrone2019-DET-val/images \
  --imgsz 1600 --coco-maxdets 100 --tag DAHP-L
```

Use `--coco-maxdets 300` for the dense-scene/native protocol. The script keeps
protocol-specific metrics separate and records checkpoint provenance where it
is available in the released result aggregate.

## Key controlled observations

| Resolution | Control | Observation |
|---:|---|---|
| 640 px | base vs. union | +0.21 AP; learnability boundary, tail remains near 0.20 |
| 960 px | exact base/random/union | 28.10 / 31.77 / 31.92 md100 AP; volume contributes +3.67 and targeted reallocation +0.15 |
| 1280 px | exact base/random/union | 34.63 / 34.72 / 35.12 md100 AP; volume +0.09, targeted residual +0.40 |
| 1600 px | five seeds per sampling arm | R-only 36.55 ± 0.21, random 36.91 ± 0.29, targeted 37.18 ± 0.18 md100 AP |
| 1920 px | same-epoch and exposure-matched | same-epoch +3.83 native AP; exposure-matched residual +0.49 native / +0.42 md100 AP |

The 30-epoch two-arm analysis is retrospective. Its Pearson correlation and
post-hoc 2.5-AP cut point describe completed runs; they are not presented as a
prospective deployment experiment.

## Label-only threshold audit

`scripts/profile_threshold_sensitivity.py` evaluates whether nearby structural
proxy weights and graph thresholds change the selected policy:

```bash
python scripts/profile_threshold_sensitivity.py \
  --label-dir data/VisDrone2019/VisDrone2019-DET-train/labels \
  --reference-size 1280 \
  --output results/eval/profile_threshold_sensitivity.json
```

The audit covers lambda values 0.4, 0.5, 0.6, and 0.7 and thresholds 0.80,
0.85, and 0.90. It is a decision-set audit only; alternative sets were not
trained and no AP sensitivity is claimed.

## Latency and memory protocol

The paper uses `scripts/bench_fps.py` with 20 warm-up images, 300 measured
images, batch 1, FP16, CUDA synchronization after each image, and an exclusive
desktop RTX 3090. Preprocessing, inference, post-processing, end-to-end time,
active/reserved CUDA memory, and host-load provenance are reported separately.
The RTX 3090 is not described as edge hardware.
