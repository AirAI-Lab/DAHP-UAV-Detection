# Reproducibility

## Released numerical evidence

`results/eval/paper_results_public.json` is the single sanitized aggregate used
to audit manuscript numbers. It contains:

- 40 evaluation rows;
- per-class and UAVDT transfer results;
- five-seed control aggregates;
- reproduced modern baselines;
- the negative-result audit;
- the retrospective early-signal analysis;
- stage-wise latency and memory measurements.

The current aggregate reports `missing_sources=[]`. Its SHA-256 checksum is
stored beside it in `paper_results_public.sha256`:

```bash
sha256sum -c results/eval/paper_results_public.sha256
```

Training checkpoints, prediction dumps, private paths, GPU UUIDs, and machine
usernames are intentionally omitted. A table value that depends on an omitted
artifact is not presented as independently reproducible from this repository.

## Reproduce the label profile

```bash
python - <<'PY'
from dahp.profiler import DatasetProfiler
profile = DatasetProfiler("configs/visdrone_example.yaml", img_size=1280).profile()
print(profile.imbalance_ratio, profile.small_object_ratio)
print([profile.class_names[c] for c in profile.tail_classes])
print([profile.class_names[c] for c in profile.confusion_axis])
PY
```

Adjust `path`, `train`, and `val` in the YAML to your local dataset layout.

## Reproduce the threshold audit

```bash
python scripts/profile_threshold_sensitivity.py \
  --label-dir data/VisDrone2019/VisDrone2019-DET-train/labels \
  --reference-size 1280 \
  --output results/eval/profile_threshold_sensitivity.json
```

The released output is `results/eval/profile_threshold_sensitivity.json`. The
equivalent UAVDT audit is `uavdt_threshold_sensitivity.json`.

## Reproduce evaluation and latency

Follow `docs/EXPERIMENT_PROTOCOL.md` for the dual-maxDets evaluator and
`docs/FPS_PROTOCOL.md` for the 300-image latency protocol. Public dataset
downloads and trained checkpoints are not redistributed in this repository.

## Environment

Create the locked environment with either:

```bash
conda env create -f environment.yml
```

or install `requirements-lock.txt` in an existing Python 3.10 environment.
