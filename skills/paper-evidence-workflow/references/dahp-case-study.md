# DAHP Case Study: From Detection Problem to Revision-Ready Manuscript

This reference distills the DAHP UAV-detection project into a reusable pattern. It records the process decisions and evidence transitions, not private infrastructure details.

## 1. Initial research object

The project began with three coupled UAV-image pathologies:

1. extreme object-scale imbalance;
2. long-tailed class frequencies;
3. structurally similar categories that interfere with one another.

Early architectural modules did not reliably improve strong baselines and often worsened localization. The project therefore shifted from “add a module” to a data-centric question:

```text
When does rebalancing help, and what part of the gain comes from
exposure, volume, or targeted class selection?
```

## 2. Establishing an objective profile

The profiler was intentionally label-only:

- no image decoding;
- no gradients;
- no model inference;
- no predicted confusion matrix.

It reports:

- class frequencies and head-tail ratio;
- tiny/small/medium object ratios;
- aspect-ratio and scale histogram overlaps;
- a structural-similarity graph;
- head-anchored confusion axis;
- resolution/backbone and oversampling policy.

This choice made the method portable from VisDrone to UAVDT without dataset-specific code edits.

## 3. Correcting the method-code-paper alignment

A critical early inconsistency was found:

- the manuscript initially described a geometric/co-occurrence confusion score;
- the implementation used aspect-ratio and scale histogram intersections.

The project was paused until the paper, code, figures, and verification script agreed on:

```text
0.6 * aspect-ratio overlap + 0.4 * scale overlap
```

The lesson: before adding experiments, verify that the claimed measurement is the implemented measurement.

## 4. From many runs to a controlled mechanism

The project accumulated many architecture and sampling attempts. Instead of selecting the best post hoc, the work was reorganized into controlled arms:

1. architecture and resolution ladder;
2. tail-only sampling;
3. confusion-axis sampling;
4. union sampling;
5. random volume control;
6. exposure-matched baseline;
7. cross-dataset transfer;
8. online prediction probe.

This converted an engineering leaderboard into evidence for a regime principle.

## 5. Negative results became a contribution

Audited failures were retained:

- seven feature-module generations;
- head-decoupling and weight-sharing variants;
- naive allocator;
- frequency sampling at 1280;
- sliced inference on full-image models;
- SAFT mixtures;
- shorter YOLO26 probes.

They supported a scoped conclusion: the tested feature-level interventions did not improve the strong baselines under matched budgets, while localization loss often worsened. Negative results were not hidden; they defined the motivation for a data-space policy.

## 6. Resolution and architecture separation

A complete YOLOv8l / YOLOv8l-P2 ladder separated architecture from resolution:

| Detector | 640 | 1280 | 1600 |
|---|---:|---:|---:|
| YOLOv8l | 23.21 | 33.76 | 37.94 |
| YOLOv8l-P2 | 27.21 | 37.96 | 39.04 |
| P2 gain | +4.0 | +4.2 | +1.1 |

This prevented the final system from being described as “zero architecture change”: P2 is an ablated architecture choice, while the sampling policy is non-invasive.

## 7. Discovering exposure as a moderator

A key apparent result was:

```text
1920 px union - base = +3.83 AP
```

A reviewer-style objection was raised: does union sampling merely increase exposure? A 120-epoch exposure-matched baseline was added:

| Arm | native AP | md100 AP | APs |
|---|---:|---:|---:|
| base@60 | 35.67 | — | — |
| union@60 | 39.50 | 37.93 | 30.46 |
| base@120 | 39.01 | 37.51 | 29.54 |

The matched residual was:

```text
+0.49 native AP
+0.42 md100 AP
+0.92 APs
```

This refined the principle: 1920 px is exposure-limited, and the same-epoch gain must not be attributed entirely to targeted sampling.

## 8. Volume versus targeted reallocation

At 1600 px, the random-volume control separated data volume from targeted union:

| Arm | n | AP |
|---|---:|---:|
| R only | 3 | 36.55 ± 0.21 |
| random volume | 5 | 36.91 ± 0.29 |
| targeted union | 3 completed | 37.09 ± 0.16 |

The current interpretation is:

```text
volume:       +0.36 AP
targeted:     +0.18 AP
```

The result is honest but not yet final; targeted union is being extended to five seeds before significance language is used.

## 9. Making the principle predictive

A single-run epoch-gain rule failed as an online discriminator and was reported as a negative control. The successful diagnostic was a two-arm early probe:

- compare treatment and matched base using only the first epochs;
- use the best-checkpoint gap;
- probe at epoch 30.

Result:

```text
Pearson r = 0.983
5/5 regime separation
threshold = 2.5 AP
```

This changed the work from retrospective regime naming to a predictive principle.

## 10. Baseline fairness evolution

The comparison table evolved through three layers:

1. same-input general detectors;
2. UAV-specific detectors;
3. same-detector mechanism controls.

Modern baselines included YOLO11, YOLO12, and YOLO26. At 640 px:

```text
DAHP-M 26.11
YOLO26-L 24.90
YOLO12-L 23.67
YOLO11-L 23.97
```

External literature values were labeled separately from reproduced values. An unpublished high-resolution comparator claim was removed from the main evidence.

## 11. Manuscript synchronization

Every completed experiment triggered synchronization of:

- fact table;
- evidence matrix;
- main table;
- ablation table;
- regime matrix;
- figure generation script;
- figure caption;
- discussion;
- conclusion;
- public repository.

Pending results remained excluded from final claims. This prevented a visually attractive but unsupported narrative from entering the manuscript.

## 12. Reusable lessons

| Lesson | Transfer |
|---|---|
| Measure before intervening | Label-only profile exposes scale, tail, and confusion |
| Test one factor at a time | Architecture, resolution, volume, targeted policy |
| Add a random-volume control | Separates “more data” from “which data” |
| Match exposure before causal claims | Essential for oversampled high-resolution runs |
| Keep failed modules auditable | Negative results can define the research gap |
| Do not mix protocols | md100 and native need separate columns |
| Use online probes | Avoid retrospective regime labeling |
| Mark pending evidence | Prevents partial runs becoming conclusions |
| Maintain bilingual documentation | Enables team review and handoff |
| Release plotting scripts | Figures remain auditable |

## 13. Pattern for the next project

1. Define phenomenon and non-goals.
2. Build a label/data profile.
3. Reproduce a strong baseline under one evaluator.
4. Create architecture/resolution ladder.
5. Add policy arms and random controls.
6. Add exposure or budget-matched controls.
7. Test online predictability.
8. Transfer the policy unchanged to a second dataset.
9. Add modern and domain baselines.
10. Audit every claim against evidence files.
11. Write Methods and Results before Introduction.
12. Prepare reviewer responses as experiments, not rhetoric.
