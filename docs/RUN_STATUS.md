# Run Status Board

Snapshot: 2026-09-18 21:42 UTC / 2026-09-19 05:42 Beijing.

## Server and queues

All listed supervisors and final-evaluation watchers are reboot-safe. The
D-FINE GPU0 retry queue was removed; D-FINE now runs alone on GPU6 with total
batch 8. GPU0 is reserved for the batch-2 RT-DETR-L control.

Our active jobs use six GPUs:

| GPU | Run | Progress | Current best AP | Status |
|---:|---|---:|---:|---|
| 0 | `base_rtdetrl_b2_640` | 21/100 epochs | native 2.646 | running alone; late convergence expected |
| 1 | `s960_base_b2` | 4/60 | native 0.108 | batch-matched 960 base |
| 3 | `cf_s46` | 72/100 | native 38.729 | targeted-union seed 46 |
| 4 | `cf_s45` | 73/100 | native 38.681 | targeted-union seed 45 |
| 5 | `rtdetr_union_640` | 44/100 | native 4.632 | RT-DETR union arm |
| 6 | `base_dfine_m_640` | epoch-1 eval passed | upstream md100 2.124 | D-FINE-M train batch 8; val batch 2 after OOM control |

GPU2 and GPU7 belong to other users.

## Completed fairness controls

- Exact 1280 base/random/union: md100 34.6296 / 34.7233 / 35.1223; native
  34.6859 / 34.7770 / 35.1772.
- Exact 1280 interpretation: volume +0.0937, targeted residual +0.3990 md100.
- Manuscript attribution table, Fig. 8, and bilingual fact/evidence documents
  now contain the exact 1280 triplet.

## Queued work

- `queue_rtdetrv2_gpu4.sh` waits for `cf_s45` and its final evaluation to
  release GPU4, then trains RT-DETRv2-L at 640 px, total batch 8, 100 epochs.
- The 960 queue evaluates `s960_base_b2` with md100 and native/md300 after
  60 epochs.
- The final-evaluation watcher will evaluate `cf_s45`, `cf_s46`, and
  `rtdetr_union_640` when each completes.

## Expected completion

Current rough estimates:

- `s960_base_b2`: about 7--8 hours at the observed average epoch time.
- `cf_s45` / `cf_s46`: about 12--13 hours plus evaluation.
- D-FINE-M: about 15--17 hours if the roughly 9-minute epoch-plus-evaluation cycle remains stable.
- Batch-2 RT-DETR-L base: about 30 hours.
- RT-DETR union: about 38--44 hours.

Server reboots and load changes can shift these estimates.

## Next actions

1. Confirm D-FINE completes the epoch-0 evaluation with validation batch 2 and
   record the steady-state epoch time.
2. Replace the three-seed 1600 targeted statistic with n=5 after seeds 45/46.
3. Add batch-matched RT-DETR base/union cross-family evidence only after both
   complete and use one evaluator.
4. Parse D-FINE / RT-DETRv2 upstream COCO logs into the common result schema.
5. Keep protocol-separated values in separate table blocks; never subtract
   md100 from native/md300.
