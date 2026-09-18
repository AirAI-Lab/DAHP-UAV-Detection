# DAHP Manuscript Fact Table

> Purpose: prevent narrative drift. Every manuscript claim must be traceable to
> an entry in this table, an evaluation JSON, or a cited paper. Items marked
> **pending** must not be stated as final results in the manuscript.

## 1. Research object and datasets

| Item | Fixed fact | Notes / evidence status |
|---|---|---|
| Primary dataset | VisDrone2019-DET | Train 6,471 images; val 548 images; 10 classes |
| Primary val instances | 38,759 boxes | Used for density and profiling statistics |
| Transfer dataset | UAVDT | Same label-only profiler, no dataset-specific retuning |
| Evaluation split | VisDrone val | test-dev is not used for the final claim because public ground truth is unavailable |
| Profiler input | Labels only | No images, gradients, model inference, or prediction confusion matrix |
| Profiler output | Long-tail, scale, and structural-confusion statistics | Maps to resolution/backbone and sampling policy |

### VisDrone profile

| Pathology | Value used in paper | Status |
|---|---:|---|
| Head-to-tail ratio | 45:1 | Verified on training labels |
| Instances <32 px at 640 reference | 85.3% | Verified |
| Head-anchored confusion axis | van, truck | Derived from structural-similarity graph |
| Pairs with structural similarity >0.85 | 23 | Verified |
| Confusion score | 0.6 aspect-ratio overlap + 0.4 scale overlap | Paper, profiler, and verification script aligned |

### UAVDT profile

| Pathology | Value | Status |
|---|---:|---|
| Head-to-tail ratio | 30.7:1 | Verified |
| Small-object ratio at 640 | 74.8% | Verified |
| Strongest confusion pair | car--van, 0.935 | Verified |
| Policy axis | van, with union set truck/bus/van | Zero-shot transfer |

## 2. Hardware and training protocol

| Item | Fact |
|---|---|
| GPU | NVIDIA RTX 3090, 24 GB |
| Main YOLO training | Ultralytics 8.4.60, PyTorch 2.5.1 + CUDA 12.1 |
| Typical schedule | 100 epochs unless explicitly stated |
| Resolution ladder | 640 / 960 / 1280 / 1600 / 1920 |
| 640 baseline batch | 8 |
| 1600 YOLOv8m-P2 controls | batch 2 |
| RT-DETR-L baseline | 640 px, batch 4, 100 epochs |
| Random seed policy | report n and std; no significance claim without enough seeds |
| Server recovery | checkpoint resume plus reboot-safe queue scripts |

Deviations such as compute-matched RemDet retraining and shorter exploratory
runs are disclosed in the manuscript or negative-result appendix.

## 3. Evaluation protocols

| Protocol | Meaning | Use |
|---|---|---|
| md100 | COCO-style AP, maxDets=100 | Cross-method main table and attribution controls |
| native/md300 | Ultralytics-style dense protocol, maxDets=300 | Native training-selection results and regime matrix |
| APs/APm/APl | COCO area ranges | Small-object evidence |
| Best checkpoint | Highest validation mAP during the declared schedule | Main results |
| Final checkpoint | Available in logs but not substituted for best checkpoint | Audit only |

Rules:

1. Never mix md100 and native numbers in one subtraction.
2. Always label reproduced, official-weight reproduction, and literature rows.
3. Literature numbers are context, not same-protocol evidence.
4. Parentheses in the main table denote the secondary native protocol.

## 4. Completed key results

### Main VisDrone results

| Configuration | Input | Protocol | AP | Notes |
|---|---:|---:|---:|---|
| DAHP-M full | 640 | md100 | 26.11 | Same-resolution modern-baseline comparison |
| YOLO26-L | 640 | md100 | 24.90 | Strongest reproduced modern YOLO baseline in current table |
| YOLO12-L | 640 | md100 | 23.67 | Completed |
| YOLO11-L | 640 | md100 | 23.97 | Completed |
| Baseline YOLOv8m-P2 | 1280 | md100 | 34.63 | Main baseline |
| DAHP-L | 1600 | md100 | 38.16 | Single model |
| DAHP-L | 1600 | native | 40.06 | Secondary protocol |
| DAHP-L E7 | 1600 | md100 | 39.61 | Ensemble, reported separately |

### Same-detector P2 ladder, native/md300

| Detector | 640 | 1280 | 1600 |
|---|---:|---:|---:|
| YOLOv8l vanilla | 23.21 | 33.76 | 37.94 |
| YOLOv8l-P2 | 27.21 | 37.96 | 39.04 |
| P2 gain | +4.0 | +4.2 | +1.1 |

### Exposure-aware attribution at 1600 px, md100

| Arm | n | AP | Tail mean |
|---|---:|---:|---:|
| R only | 3 | 36.55 ± 0.21 | 0.339 |
| Random volume control | 5 | 36.91 ± 0.29 | 0.341 |
| Targeted union | 3 completed | 37.09 ± 0.16 | 0.346 |

Current interpretation: volume explains +0.36 AP; targeted reallocation adds a
+0.18 AP residual. Two additional targeted seeds are running and must replace
this three-seed entry when complete.

### 1920 px exposure-matched control

| Arm | Schedule | native AP | md100 AP | APs |
|---|---:|---:|---:|---:|
| Base | 60 ep | 35.67 | not the matched comparison | — |
| Union | 60 ep | 39.50 | 37.93 | 30.46 |
| Base | 120 ep | 39.01 | 37.51 | 29.54 |
| Matched residual | union60 - base120 | +0.49 | +0.42 | +0.92 |

Conclusion: the same-epoch +3.83 AP should not be described as targeted
sampling alone; most of it is exposure.

### Online two-arm prediction

| Diagnostic | Result |
|---|---:|
| Probe epoch | 30 |
| Pearson correlation with final gain | 0.983 |
| Positive/saturated separation | 5/5 |
| Threshold | probe gap >2.5 AP |
| Negative control | single-arm epoch-gain statistic does not discriminate regimes |

### UAVDT transfer

| Arm | AP | Tail |
|---|---:|---:|
| Base | 37.86 | 32.05 |
| Frequency-only | 37.80 | 31.49 |
| Union | 38.55 | 33.73 |

## 5. Pending facts that must not be finalized yet

| Pending item | Current purpose | Required before final claim |
|---|---|---|
| Targeted union seeds 4--5 | Upgrade targeted arm to n=5 | 100 epochs + md100 evaluation |
| Exact 1280 union and random controls | Replace frequency proxy in regime matrix | 100 epochs + md100/native evaluation |
| RT-DETR union arm | Detector-family independence | converged training and unified evaluation |
| D-FINE / RT-DETRv2 baselines | Optional but reviewer-relevant modern DETR comparison | install/train under disclosed budget or clearly scope out |
| VisDrone test-dev | External benchmark claim | challenge-server evaluation; otherwise keep val-set limitation |
| Expanded FPS protocol | Stronger efficiency evidence | preprocessing/inference/postprocess breakdown and >=200 images |

## 6. Claim vocabulary rules

| Forbidden / discouraged | Preferred |
|---|---|
| state of the art by X AP without protocol | strongest reproduced comparator under our protocol |
| zero architecture change for the whole system | the rebalancing policy itself adds no architectural modification |
| rebalancing law | exposure-aware regime-dependent rebalancing principle |
| union gives +3.83 AP at 1920 | same-epoch gain is +3.83; exposure-matched residual is +0.42 md100 |
| edge real-time | real-time on a desktop RTX 3090 |
| statistically significant with n<5 | report n, mean, std, and paired differences; use CI when justified |
