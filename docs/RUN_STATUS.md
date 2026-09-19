# Run Status Board

Snapshot: 2026-09-19 13:44 UTC / 21:44 Beijing.

## Server and queues

The server has been up for 6 h 14 m after its scheduled reboot. All listed
supervisors recovered automatically and the monitored queue logs contain no new
OOM, traceback, or failure.

Our active jobs use five GPUs:

| GPU | Run | Progress | Current best AP | Status |
|---:|---|---:|---:|---|
| 0 | `base_rtdetrl_b2_640` | 54/100 | native 4.841 | batch-2 RT-DETR-L control |
| 1 | `s960_rand_b2` | 21/60 | native 31.075 | exact random-volume control |
| 4 | `base_rtdetrv2_l_640` | restarted epoch 0 | pending | category mapping fixed; total batch 8 |
| 5 | `rtdetr_union_640` | 61/100 | native 4.907 | RT-DETR union arm |
| 6 | `base_dfine_m_640` | 89/100 logged | corrected md100 31.532 @ ep86 | COCO category remap fixed |

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

## Expected completion

- D-FINE-M: about 1--2 hours for the remaining logged epochs, plus final audit.
- `s960_rand_b2`: about 8--11 hours depending on load.
- Batch-2 RT-DETR-L base: about 17--20 hours.
- RT-DETR union: about 15--22 hours depending on load.
- RT-DETRv2-L: newly started; estimate after epoch 0--2 stabilizes.

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
