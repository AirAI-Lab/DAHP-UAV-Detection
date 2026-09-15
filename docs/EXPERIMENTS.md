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
4. **Seed stability**: key configurations are run with 2-3 seeds; std is
   reported next to the mean.
5. **No inference-time modification** for the proposed method: DAHP changes
   only training data and training-time configuration.

## Resolution-regime ladder

For each resolution (640 / 960 / 1280 / 1600 / 1920) the following are
trained: a base model and a union-sampling variant (matched epochs). The
difference dAP as a function of resolution characterizes the regime:

- 640: dAP ~ +0.2 (learnability lower bound; tail objects unresolvable)
- 960: dAP ~ +3.2 (under-fitted; sampling strongly positive-sum)
- 1280: dAP ~ 0 (saturated; reallocation is zero-sum)
- 1600: dAP ~ +1.0 (sweet spot used in the paper)
- 1920: dAP ~ +3.8 (exposure-limited; doubling per-epoch exposure rescues)

## UAVDT transfer

The same profiler + union-sampling recipe is applied to UAVDT without
retuning: oversampled classes {truck, bus, van}. Result: +0.69 AP overall,
+1.69 AP on tail classes; frequency-only sampling is ineffective,
matching the regime prediction.

## Negative results (disclosed in the paper)

- Pure tiled/sliced inference on full-image-trained models: -2.3 to -2.6 AP.
- Frequency-only sampling at 1280: ~0 gain (saturated regime).
- Loss-space interventions (EQLv2-style reweighting) on strong baselines:
  approximately zero-sum at saturation.

## Efficiency

All latency numbers: single RTX 3090, batch 1, FP16, conf 0.25, 50 measured
images after 10 warmup images (`scripts/bench_fps.py`).
