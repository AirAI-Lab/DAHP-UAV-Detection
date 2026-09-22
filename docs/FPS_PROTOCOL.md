# FPS, Latency, and Memory Protocol

## Scope

The reported efficiency measurements describe desktop-GPU inference, not edge
deployment. They are intended to expose the cost of input size and the P2 head
under one controlled protocol.

## Hardware and runtime

| Item | Value |
|---|---|
| GPU | 1 × NVIDIA GeForce RTX 3090 (24 GB), exclusive during measurement |
| CPU | 24 cores; one-minute load recorded before and after the run |
| Precision | FP16 |
| Batch | 1 |
| Images | 20 warm-up, 300 measured VisDrone-val images |
| Synchronization | CUDA synchronize after every image |
| Confidence | 0.25 |

## Measured stages

`scripts/bench_fps.py` records:

1. preprocessing time reported by Ultralytics;
2. detector inference time;
3. post-processing/NMS time;
4. aggregate end-to-end wall time over all measured images;
5. pipeline residual, defined as end-to-end minus the stage sum;
6. active and reserved CUDA memory after warm-up;
7. parameter count and host-load provenance.

A run is paper-eligible only when the GPU is exclusive at start and finish, at
least 200 images are measured, and all required stages are present. Shared-GPU
smoke tests are not paper measurements.

## Command

```bash
python scripts/bench_fps.py \
  --val-dir data/VisDrone2019/VisDrone2019-DET-val/images \
  --device 0 --warmup 20 --measure 300 --require-exclusive \
  --tags baseline_v8mP2_1280,vanilla_v8l_1600,v8lP2_1600,dahpL_1600 \
  --output results/eval/fps_benchmark_300.json
```

`scripts/validate_fps_result.py` checks eligibility before a result is used.

## Reported result

The final aggregate is embedded in `results/eval/paper_results_public.json`.
DAHP-L measures 38.0215 ms end-to-end and 26.3009 FPS, with 7.325 ms
preprocessing, 24.405 ms inference, 1.537 ms post-processing, 4.754 ms pipeline
residual, and 0.348/0.670 GB active/reserved CUDA memory. The same-architecture
YOLOv8l-P2 control measures 39.5982 ms and 25.2537 FPS; the small difference is
not claimed as a policy speedup. Host load was elevated, making end-to-end
timings conservative.
