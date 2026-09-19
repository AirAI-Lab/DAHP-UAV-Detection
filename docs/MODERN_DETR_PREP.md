# Modern DETR Baseline Preparation

Snapshot: 2026-09-18.

## Purpose

Prepare D-FINE and RT-DETRv2 baselines without waiting for server GitHub access. Source and pretrained checkpoints were downloaded locally and transferred to the server.

## Source versions

| Model | Upstream | Version | Checkpoint |
|---|---|---|---|
| D-FINE-M | `Peterande/D-FINE` | `956d1709314c2c6a4df6f34de232054578a7449f` | `dfine_m_obj2coco.pth` |
| RT-DETRv2-L | `lyuwenyu/RT-DETR`, `rtdetrv2_pytorch` subset | `29320b6fd828f8e0987a71426cf2d961b09dfed7` | `rtdetrv2_r50vd_6x_coco_ema.pth` |

Server locations:

```text
/home/wn/wn/edge_infer_cloud/third_party/visdrone_staging/dfine
/home/wn/wn/edge_infer_cloud/third_party/visdrone_staging/rtdetrv2
/home/wn/wn/edge_infer_cloud/third_party/visdrone_staging/weights
```

## Dataset conversion

The upstream trainers use COCO JSON, whereas the project stores VisDrone in YOLO format. `scripts/build_coco_from_yolo.py` was added and used to create:

```text
visdrone_train_coco_dedup.json
  6,471 images
  343,200 annotations
  4 exact duplicate boxes removed

visdrone_val_coco.json
  548 images
  38,759 annotations
```

The training file removes exact duplicate YOLO lines. The validation file preserves the existing evaluation convention.

## Protocol

Both prepared baselines use:

```text
input: 640
training total batch: 8
epochs: 100
seed: 0
AMP: enabled
network input: fixed 640x640 (upstream multi-scale collation disabled)
D-FINE validation batch: 2
D-FINE GPU: 6
RT-DETRv2 GPU: 4, after cf_s45 and its final evaluation release it
```

D-FINE uses the Objects365+COCO checkpoint for tuning. RT-DETRv2 uses the official COCO EMA checkpoint for tuning. Mismatched classification heads are intentionally reinitialized by each upstream tuning path. D-FINE evaluation uses batch 2 only to avoid OOM while another user occupies part of GPU6; this does not change the training batch or optimizer exposure.

## Smoke checks completed

- D-FINE Python/config import: passed.
- RT-DETRv2 Python/config import: passed.
- D-FINE dataset counts: 6,471 train / 548 val.
- RT-DETRv2 dataset counts: 6,471 train / 548 val.
- D-FINE parameters after head setup: 19.48M.
- RT-DETRv2 parameters after head setup: 42.75M.
- D-FINE checkpoint tuning load: passed.
- RT-DETRv2 checkpoint tuning load: passed.
- First training batch shape for both trainers: `(8, 3, 640, 640)`.
- RT-DETRv2 accidental backbone download disabled with `PResNet.pretrained: False`.

## D-FINE evaluator correction

A batch-8 validation sanity check exposed a COCO category-ID mismatch. D-FINE
outputs zero-based detector labels, while the VisDrone COCO ground truth uses
category IDs 1--10. The upstream evaluator passed labels through without the
dataset-specific `label2category` remap, producing invalid AP values despite
reasonable box/class diagnostics. Training and loss were unaffected.

`src/solver/det_engine.py` now converts detector labels through
`data_loader.dataset.label2category` only for COCO evaluation; the lightweight
validator continues to use zero-based labels. On checkpoint 49:

| Evaluator | AP | AP50 | APs |
|---|---:|---:|---:|
| Before remap, validation batch 8 | 2.8 | 4.9 | 2.2 |
| After remap, validation batch 8 | 30.2 | 49.1 | 20.2 |

Training resumed from epoch 50 with the corrected evaluator. Logged AP values
before this point are audit history and must not enter the paper.

### D-FINE stage-2 accounting correction

Upstream D-FINE uses a two-stage schedule and logs epochs 1--99 for a declared
100-epoch schedule. The first queue supervisor mistakenly used physical log-line
count, saw 99 lines after completion, and relaunched stage 2 from the epoch-71
stage-one checkpoint. The duplicate rows were archived rather than deleted, the
clean log was restored to epochs 1--71, and the queue now tracks maximum logged
epoch. Stage 2 is being rerun exactly once; only this clean pass will be used
for the final D-FINE row.

## RT-DETRv2 category-mapping correction

The first RT-DETRv2 launch repeated a device-side index assertion. The cause
was the same 1-based COCO category-ID versus 0-based detector-label mismatch:
VisDrone category ID 10 indexed outside a 10-class head. Two paths were fixed:

1. `src/data/dataset/coco_dataset.py` maps declared category IDs through
   `category2label` for training targets.
2. `src/solver/det_engine.py` maps detector labels through `label2category`
   only for COCO evaluation.

The failed epoch-0 run directory was removed, the queue now backs off for
300 seconds after a nonzero exit, and training restarted cleanly from epoch 0.
The restarted process has had no category-index assertion.

## Queue

`scripts/queue_dfine_gpu6.sh` is running and reboot-safe. It resumed from the epoch-0 checkpoint after the evaluation OOM, evaluates with batch 2, and resumed from epoch 50 after the COCO category-mapping fix. `scripts/queue_rtdetrv2_gpu4.sh` restarted RT-DETRv2 from epoch 0 after its category-mapping fix and now backs off after failures.

No new GPU is occupied at preparation time.
