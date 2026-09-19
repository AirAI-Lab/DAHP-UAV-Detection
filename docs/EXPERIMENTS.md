# Experimental Protocol

## Fair-comparison rules

1. **Matched epochs and batch budget** wherever computationally possible;
   deviations are disclosed in the manuscript.
2. **Dual evaluation protocols**: COCO-style AP with `maxDets=100`
   (md100, sparse protocol used for ablations) and `maxDets=300`
   (native/ultralytics protocol used for the main table). Both are reported
   to avoid protocol cherry-picking.
3. **Reproduction vs. literature numbers**: external methods are labelled
   `Lit.` (published number) or `Rep.` (our reproduction under the stated
   conditions). High-resolution literature numbers that could not be
   reproduced with released weights are marked separately.
4. **Seed stability**: key volume controls use five seeds; targeted union is
   being extended from three to five seeds. Report n, mean, and std.
5. **No inference-time modification** for the proposed method: DAHP changes
   only training data and training-time configuration.

## Resolution-regime ladder

For each resolution (640 / 960 / 1280 / 1600 / 1920) the following are
trained: a base model and a union-sampling variant (matched epochs). The
difference dAP as a function of resolution characterizes the regime:

- 640: dAP ~ +0.2 (learnability lower bound; tail objects unresolvable)
- 960: new batch-matched base/union = 28.10/31.92 md100 AP (+3.82);
  native = 28.17/31.98 (+3.81); APs +4.16 and tail mean +4.77
- 1280: exact same-evaluator base/random/union = 34.63/34.72/35.12 md100 AP;
  volume is nearly saturated (+0.09), while targeted union retains +0.40 over
  random (volume-saturated, not strictly zero-sum)
- 1600: same-epoch dAP +0.78 on the matched YOLOv8m-P2 family; md100 decomposition is random volume +0.36 and targeted residual +0.18
- 1920: same-epoch dAP +3.83, but the 120-epoch exposure-matched residual is +0.49 native / +0.42 md100 (+0.92 APs)

## UAVDT transfer

The same profiler + union-sampling recipe is applied to UAVDT without
retuning: oversampled classes {truck, bus, van}. Result: +0.69 AP overall,
+1.69 AP on tail classes; frequency-only sampling is ineffective,
matching the regime prediction.

## Negative results (disclosed in the paper)

- Pure tiled/sliced inference on full-image-trained models: -2.3 to -2.6 AP.
- Frequency-only sampling at 1280: ~0 gain in the legacy native series; the
  exact md100 triplet above separates volume saturation from the targeted
  residual.
- Loss-space interventions (EQLv2-style reweighting) on strong baselines:
  approximately zero-sum once indiscriminate volume/reweighting headroom is
  exhausted.

## Efficiency

All latency numbers: single RTX 3090, batch 1, FP16, conf 0.25, 50 measured
images after 10 warmup images (`scripts/bench_fps.py`).

## Current completion status

Completed: modern YOLO11/YOLO12/YOLO26 baselines, complete YOLOv8l/P2 ladder,
1920 exposure-matched control, five random-volume seeds, exact 1280
base/random/union controls, UAVDT transfer, and online two-arm prediction.
The exact 960 batch-matched base/union control is also complete.

Pending final insertion: targeted-union seeds 4--5, the exact 960 random-volume
control, batch-matched RT-DETR base/union, and the running D-FINE / RT-DETRv2
baselines. D-FINE's first 50 logged COCO AP values used an invalid category-ID
mapping and are retained only as audit history; epoch 51 is the first corrected
logged evaluation.
