# Revision Evidence Matrix and Audit

> This document answers one question: **does the current evidence support the
> paper's scientific claim under fair and complete comparisons?** It is a
> living audit table. Do not turn a `pending` row into a manuscript claim.

## 1. One-sentence thesis

UAV detection accuracy is governed by coupled long-tail, scale, and exposure
regimes; a label-only profile can identify useful non-invasive training
policies, but rebalancing helps only when exposure headroom, learnability, and
model regime permit, with targeted reallocation contributing a smaller residual
after volume effects are controlled.

## 2. Research-question evidence matrix

| # | Research question | Evidence available | Fairness control | Status | Remaining work |
|---|---|---|---|---|---|
| RQ1 | Does scale pathology dominate baseline behavior? | 85.3% <32 px; complete YOLOv8l vs P2 ladder at 640/1280/1600 | Same detector family and native/md300 evaluator | **Supported** | None |
| RQ2 | Are long tail and structural confusion measurable from labels only? | 45:1 ratio, 23 high-similarity pairs, van/truck axis; UAVDT profile | Label-only profiler verified against paper formula | **Supported** | Keep code/formula/figure synchronized |
| RQ3 | Does rebalancing effectiveness depend on regime? | 640/960/1600/1920 arms; exact 960 pair 28.10/31.92 md100; exact 1280 triplet 34.63/34.72/35.12 md100; online probe r=0.983 | Matched detector, epochs, batch, and evaluation for exact 960/1280 controls | **Supported with single-seed exact-control caveat** | Optionally replicate exact controls |
| RQ4 | Is the gain caused by volume/exposure or targeted sampling? | Exact 960 union +3.82; exact 1280: volume +0.09, targeted +0.40; 1600 md100: R 36.55, random 36.91, targeted 37.09; 1920 exposure-matched control | Volume-matched random controls and 120-epoch base control | **Partially supported** | Finish targeted n=5 at 1600; exact 960 random control running |
| RQ5 | Is the principle predictive rather than post hoc? | 30-epoch two-arm probe, r=0.983, 5/5 separation | Uses only early epochs; failed single-arm control disclosed | **Supported** | Optional prospective decision simulation |
| RQ6 | Does the policy transfer across datasets? | UAVDT union +0.69 AP, tail +1.69; frequency-only ineffective | Same profiler and recipe, no retuning | **Supported** | None unless more datasets requested |
| RQ7 | Is the policy detector-family independent? | RT-DETR base complete; RT-DETR union in progress | Same 640 px / 100 ep budget | **Pending** | Finish and evaluate RT-DETR union |
| RQ8 | Does DAHP beat modern general detectors under same input? | DAHP-M 26.11 vs YOLO26-L 24.90 at 640 md100 | Same val, epochs, evaluator | **Supported for current YOLO set** | D-FINE running; RT-DETRv2 queued |
| RQ9 | Does it beat UAV-specific detectors? | RemDet reproduced 29.90; DAHP-L 38.16 md100 | Reproduced protocol and compute-matched retrain | **Supported under reproduced protocol** | Literature high-res rows remain context only |
| RQ10 | Are architecture-first interventions reliably ineffective here? | Seven module generations and negative-result appendix | Matched 100-epoch runs and DFL audit | **Supported as scoped negative result** | Do not generalize beyond tested modules |
| RQ11 | Is inference cost honestly reported? | 24.5 FPS on RTX 3090 at 1600 | Batch 1, FP16 | **Partially supported** | Add >=200-image stage-wise latency |
| RQ12 | Is the benchmark externally complete? | VisDrone val and UAVDT | Dual protocol and Rep/Lit labels | **Partially supported** | test-dev unavailable; scope as validation protocol |

## 3. Reviewer-risk audit

| Reviewer concern | Current response | Evidence strength | Action |
|---|---|---|---|
| Paper/code formula mismatch | Equation, profiler, verification script, and figure use 0.6 AR + 0.4 scale structural similarity | Strong | Keep verification result in release |
| P2/resolution policy mismatch | Paper ladder and code ladder aligned; architecture ladder complete | Strong | None |
| Principle is retrospective | Changed from law to principle; online two-arm probe added | Strong | Optional prospective simulation |
| Exposure/capacity/learnability confounded | 640 learnability, exact 1280 volume/targeted decomposition, 1920 exposure matching, complete capacity ladder | Strong | Keep protocols separated |
| SOTA claim too strong | Removed unpublished high-res RemDet claim; wording is strongest reproduced comparator | Strong | Keep literature rows separate |
| Modern baselines missing | YOLO11/12/26 and RT-DETR-L included; D-FINE running and RT-DETRv2 queued; D-FINE category mapping fixed | Moderate | Complete and evaluate both DETR baselines |
| Too few seeds | Random n=5; targeted n=3 currently | Moderate | Two targeted seeds running |
| Zero architecture change ambiguous | Policy adds no architecture change; P2 disclosed and ablated | Strong | Keep exact wording |
| Efficiency overclaim | Desktop-GPU phrasing, no edge claim | Moderate | Upgrade latency protocol |
| Negative results not auditable | Appendix audit and logs | Strong | Release result JSON/configs |
| Confusion terminology inconsistent | Annotation-level structural similarity used consistently | Strong | Avoid appearance-confusion wording |
| Reproducibility | Public code, scripts, manuscript, figures | Moderate | Add machine-readable final-result summary |

## 4. Theory-support assessment

### Supported mechanisms

1. **Learnability lower bound.** At 640 px, duplication gives only +0.21 AP and
   tail performance remains unchanged.
2. **Volume-driven rescue.** At 960 px, the batch-matched pair gives +3.82 md100 AP,
   +4.16 APs, and +4.77 tail-mean points.
3. **Volume-saturated behavior.** Exact 1280 controls give base/random/union =
   34.63/34.72/35.12 md100 AP: random volume is nearly neutral, while targeted
   union retains a +0.40 AP residual.
4. **Intermediate positive-sum window.** At 1600 px, random duplication and
   targeted union both improve md100 AP. Current decomposition: volume +0.36,
   targeted +0.18.
5. **Exposure-limited regime.** At 1920 px, the same-epoch union gain is +3.83,
   but the 120-epoch base closes most of the gap; residual is +0.42 md100 and
   +0.92 APs.

### Current theory verdict

| Criterion | Verdict | Reason |
|---|---|---|
| Theoretically coherent | Yes | Learnability, exposure headroom, capacity, and measured controls are separated |
| Empirically supported | Mostly | All five resolution cells have controls; exact 1280 is one seed per arm |
| Predictive | Yes | Online two-arm probe r=0.983 |
| Mechanistic | Mostly | Volume and exposure controls separate causes |
| Generalization | Partial | Cross-dataset yes; detector-family independence pending |

## 5. Fairness audit

### Matched dimensions

| Dimension | Status |
|---|---|
| Validation split | Same VisDrone val images and labels for reproduced rows |
| Evaluation implementation | Same evaluator for reproduced rows; md100/native separated |
| Literature values | Explicitly labeled and not mixed into subtraction |
| Input resolution | Same-input 640 comparison exists for DAHP-M vs YOLO11/12/26 |
| Training schedule | 100 epochs for main baselines unless disclosed |
| Architecture disclosure | P2 separated from sampling policy |
| Exposure | Random-volume and 120-epoch matched controls added |
| Seeds | Random n=5; targeted n=3 pending n=5 |
| Parameters/input | Listed |
| Official weights | RemDet official-weight evaluation included |

### Known deviations and required wording

| Deviation | Why it exists | Required wording |
|---|---|---|
| DAHP-L uses 1600 px while many baselines use 640 px | Resolution is part of policy | Do not claim algorithm-only gain across this row; use DAHP-M@640 or ladder |
| RT-DETR requested 640 but trains effective 1280 | Ultralytics behavior | Disclose in footnote |
| RemDet 1600 retrain uses single-GPU compute match | Compute control | Already disclosed |
| 1920 union doubles per-epoch exposure | Exposure is part of mechanism | Report same-epoch and exposure-matched effects separately |
| Literature rows differ in protocol | Not all setups reproducible | Label Lit. and split/test-dev |
| test-dev GT unavailable | Benchmark limitation | Say validation protocol, not official benchmark SOTA |

## 6. Completeness checklist

### Done

- [x] Label-only profiler formula/code alignment
- [x] Resolution ladder 640/960/1280/1600/1920
- [x] Complete YOLOv8l vanilla versus P2 ladder
- [x] YOLO11/12/26 modern baselines
- [x] RT-DETR-L base
- [x] RemDet official-weight and compute-matched evaluation
- [x] UAV-specific literature comparison
- [x] UAVDT transfer
- [x] Negative-result appendix
- [x] Online regime prediction
- [x] 1920 exposure-matched control
- [x] Five-seed random-volume control
- [x] Exact 1280 base/random/union controls
- [x] Exact 960 batch-matched base/union controls
- [x] Fig. 8 regenerated with the exact 1280 decomposition
- [x] Dual evaluation protocols
- [x] Public repository and manuscript synchronization

### Must finish before calling the revision complete

- [ ] Targeted union n=5
- [ ] RT-DETR union cross-family result
- [ ] Final attribution table after all n=5 seeds
- [ ] Machine-readable release of final evaluation JSON/configs

### Strongly recommended if time permits

- [ ] D-FINE baseline (running)
- [ ] RT-DETRv2 baseline (queued on GPU4)
- [ ] Expanded FPS protocol
- [ ] Prospective online-policy simulation
- [ ] test-dev challenge submission if possible

## 7. Claim language allowed now

| Claim | Allowed? | Exact wording |
|---|---|---|
| DAHP-M beats reproduced YOLO26-L at 640 | Yes | 26.11 vs 24.90 md100 under identical validation protocol |
| DAHP-L beats strongest reproduced UAV detector under our protocol | Yes | 38.16 vs 29.90 md100 with disclosed resolution/capacity policy |
| Union causes +3.83 at 1920 | Not alone | Same-epoch gain is +3.83; exposure-matched residual is +0.42 md100 |
| Exact 1280 union beats random | Yes, with seed disclosure | +0.40 md100 AP over random in a one-seed-per-arm matched triplet |
| Targeted union significantly beats random | Not yet | Directionally +0.18 with n=3; wait for n=5 |
| Detector-family independence | Not yet | RT-DETR union pending |
| Official VisDrone SOTA | No | Validation-set protocol only |
| Edge real-time | No | Desktop RTX 3090 real-time |
