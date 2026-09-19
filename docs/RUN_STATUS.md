# Run Status Board

Snapshot: 2026-09-19 08:29 UTC / 16:29 Beijing.

## Server and queues

All listed supervisors and final-evaluation watchers are reboot-safe. The
D-FINE GPU0 retry queue was removed; D-FINE now runs alone on GPU6 with total
batch 8. GPU0 is reserved for the batch-2 RT-DETR-L control.

Our active jobs use six GPUs:

| GPU | Run | Progress | Current best AP | Status |
|---:|---|---:|---:|---|
| 0 | `base_rtdetrl_b2_640` | 39/100 epochs | native 3.804 | running alone; late convergence expected |
| 1 | `s960_rand_b2` | launched 0/60 | pending | exact random-volume control for 960 |
| 3 | `cf_s46` | 88/100 | native 38.729 | targeted-union seed 46 |
| 4 | `cf_s45` | 88/100 | native 38.681 | targeted-union seed 45 |
| 5 | `rtdetr_union_640` | 53/100 | native 4.632 | RT-DETR union arm |
| 6 | `base_dfine_m_640` | resumed at 50/100 | corrected ckpt-49 AP 30.2 | COCO category mapping fixed; train batch 8 |

`s960_base_b2` completed all 60 epochs. Its released GPU1 is now used by the
exact 960 random-volume control. GPU2 and GPU7 belong to other users.

## Completed fairness controls

- Exact 1280 base/random/union: md100 34.6296 / 34.7233 / 35.1223; native
  34.6859 / 34.7770 / 35.1772.
- Exact 1280 interpretation: volume +0.0937, targeted residual +0.3990 md100.
- Exact 960 batch-matched base/union: md100 28.1009/31.9239 (+3.8231);
  native 28.1722/31.9794 (+3.8072); APs +4.1603; tail mean +4.7704.
- The matching 960 random-volume arm uses the same 12,276-image exposure,
  batch 2, 60 epochs, and seed 0; it will separate volume from targeted
  reallocation without relying on the legacy 77/23 decomposition.
- D-FINE COCO category-ID remap fixed. Checkpoint 49 changes from invalid
  AP 2.8 to corrected AP 30.2 under validation batch 8.
- Manuscript attribution table, Fig. 8, and bilingual fact/evidence documents
  now contain the exact 1280 triplet.

## Queued work

- `queue_rtdetrv2_gpu4.sh` waits for `cf_s45` and its final evaluation to
  release GPU4, then trains RT-DETRv2-L at 640 px, total batch 8, 100 epochs.
- The final-evaluation watcher will evaluate `cf_s45`, `cf_s46`, and
  `rtdetr_union_640` when each completes.

## Expected completion

Current rough estimates:

- `cf_s45` / `cf_s46`: about 5--6 hours plus evaluation at current speed.
- D-FINE-M: about 8--9 hours from epoch 50.
- Batch-2 RT-DETR-L base: about 22--24 hours.
- RT-DETR union: about 25--35 hours depending on load.

Server reboots and load changes can shift these estimates.

## Next actions

1. Replace the three-seed 1600 targeted statistic with n=5 after seeds 45/46.
2. Insert the exact 960 random-volume terminal value when it completes.
3. Add batch-matched RT-DETR base/union cross-family evidence only after both
   complete and use one evaluator.
4. Parse D-FINE / RT-DETRv2 upstream COCO logs into the common result schema.
5. Keep protocol-separated values in separate table blocks; never subtract
   md100 from native/md300.
