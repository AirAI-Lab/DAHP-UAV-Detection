# Run Status Board

Snapshot: 2026-09-19 16:40 UTC / 2026-09-20 00:40 Beijing.

## Server and queues

The server has been up for 6 h 14 m after its scheduled reboot. All listed
supervisors recovered automatically and the monitored queue logs contain no new
OOM, traceback, or failure.

Our active jobs use five GPUs:

| GPU | Run | Progress | Current best AP | Status |
|---:|---|---:|---:|---|
| 0 | `base_rtdetrl_b2_640` | 61/100 | native 5.656 | batch-2 RT-DETR-L control |
| 1 | `s960_rand_b2` | 31/60 | native 32.262 | exact random-volume control |
| 4 | `base_rtdetrv2_l_640` | 10/100 | corrected md100 24.654 | category mapping fixed; total batch 8 |
| 5 | `rtdetr_union_640` | 65/100 | native 4.907 | RT-DETR union arm |
| 6 | `base_dfine_m_640` | clean stage-2 restart from logged ep71 | pending final | queue epoch accounting corrected |

GPU2, GPU3, and GPU7 are not part of our active allocation at this snapshot.
GPU4 also contains another user's process, but the RT-DETRv2 allocation remains
within the disclosed budget.

## Completed since the last board

- `cf_s45`: 100/100; native best 38.681.
- `cf_s46`: 100/100; native best 38.729.
- Final md100/native evaluations for both seeds completed.
- Targeted union at 1600 px is now n=5:
  - R only: 36.548 ± 0.207;
  - random volume: 36.906 ± 0.286;
  - targeted union: 37.181 ± 0.178.
- Decomposition: volume +0.358, targeted residual +0.275 AP. This is
  directional evidence, not a significance claim.
- D-FINE evaluator was corrected for VisDrone category IDs. Only epoch 51
  onward is valid for COCO log AP.
- RT-DETRv2 hit the same category-ID mismatch and was fixed before any valid
  epoch completed. Its failed epoch-0 artifacts were removed and training
  restarted cleanly.
- D-FINE completed one stage-2 pass, but the queue used physical log-line count
  rather than maximum epoch and relaunched stage 2 from epoch 72. The duplicate
  rows were archived in `log.duplicate_stage2_20260919.jsonl`, the clean log was
  restored to epochs 1--71, and stage 2 is being rerun exactly once for the
  final paper result.

## Expected completion

- D-FINE-M clean stage 2: about 4--5 hours, plus final audit.
- `s960_rand_b2`: about 7--9 hours depending on load.
- Batch-2 RT-DETR-L base: about 14--17 hours.
- RT-DETR union: about 18--24 hours depending on load.
- RT-DETRv2-L: about 20--26 hours at the observed early speed.

## Next actions

1. Run the D-FINE final batch-8 validation audit and parse the corrected COCO
   result into the common result schema.
2. Insert `s960_rand_b2` when it completes to replace the legacy 77/23
   decomposition with an exact same-protocol triplet.
3. Wait for batch-matched RT-DETR base/union before making the
   detector-family claim.
4. Track RT-DETRv2 through its early epochs and adapt its evaluator output.
5. Keep native/md300 and md100 blocks separate; never mix protocols in a
   subtraction.
