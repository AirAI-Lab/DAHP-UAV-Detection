# Reusable SCI Paper Process Playbook

This playbook distills the process used for the DAHP UAV-detection manuscript.
It emphasizes an unbroken evidence chain from raw runs to manuscript claims.

## 0. Non-negotiable principles

1. **Facts before narrative.** Build an objective fact table before writing.
2. **Evidence before claims.** Every number needs a source and protocol.
3. **Controls before explanation.** Separate architecture, resolution,
   exposure, and targeted policy.
4. **Fairness before leaderboard.** Same split/protocol first; literature
   numbers are contextual.
5. **Honest limitations.** A bounded claim is stronger than an overbroad claim.
6. **Reproducibility.** Release code, configs, seeds, scripts, and summaries.
7. **Accountable authorship.** Authors verify every parameter, citation, result, interpretation, and final claim.

## 1. Day 1: objective fact table

Create `docs/FACT_TABLE.md` before writing prose.

Required fields:

- task objective;
- datasets, splits, class taxonomy, preprocessing;
- train/val/test image and instance counts;
- hardware, OS, package versions;
- model family, checkpoint source, parameter count;
- optimizer, learning rate, batch, epochs, seed;
- augmentation;
- metric and exact evaluation protocol;
- latency protocol;
- completed results;
- pending results;
- known deviations.

Rules:

- Unknown values are `PENDING`, never guessed.
- Every result is attached to a run or JSON identifier.
- If two protocols exist, use separate columns; never subtract across them.

Template:

```markdown
| Item | Fact | Source | Status |
|---|---|---|---|
| Dataset / split | ... | dataset YAML | fixed |
| Training schedule | ... | args.yaml | fixed |
| Metric | ... | eval script | fixed |
| Main result | ... | results/eval/*.json | complete or pending |
```

## 2. Day 2: literature evidence matrix

Do not generate citations from memory. Authors first verify papers in Zotero,
IEEE Xplore, arXiv, PubMed, or publisher pages; formatting tools may handle
only verified sources.

Template:

| Claim | Citation key | Evidence type | Setting | Limitation | Use |
|---|---|---|---|---|---|
| UAV imagery is small-object dominated | `visdrone` | dataset paper | VisDrone | protocol differs | Intro |
| Cropping can improve effective pixels | `clusdet`, `dmnet` | method papers | UAV benchmarks | bundles cropping and detector | Related work |

Audit rules:

- no DOI or stable URL, no entry;
- no unpublished claim as primary evidence;
- distinguish val, test-dev, and challenge results;
- record input size and protocol when available;
- do not extend a claim beyond the cited experiment.

## 3. Define a one-sentence thesis

Write the one sentence the whole paper must prove. Every section and figure
must support it.

DAHP example:

> Label-only profiling reveals when non-invasive UAV-detection rebalancing
> helps, but the effect is regime-dependent and must be separated from
> architecture, volume, and exposure.

Use this sentence to test the title, abstract, contributions, figures, and
conclusion.

## 4. Build the experiment design matrix

Map every research question to a minimal controlled comparison before adding
experiments.

| RQ | Hypothesis | Treatment | Control | Fixed variables | Metric | Seeds | Decision rule |
|---|---|---|---|---|---|---|---|
| Does exposure drive apparent gain? | Gain shrinks after matching | Union@60 | Base@120 | model/images/evaluator | AP/APs | >=3 | Report same-epoch and matched effects |
| Does targeted sampling add residual? | Targeted > random | Union farm | Random volume farm | model/epochs/image count | AP/tail | 5 each | Mean, std, paired effect |

Stop adding experiments when each RQ is supported, explicitly scoped out, or
marked future work and not used in the claim.

## 5. Fair comparison design

### 5.1 Baseline tiers

Use three tiers rather than one overloaded table:

1. **General real-time detectors**
   - YOLOv8, YOLO11, YOLO12, YOLO26, RT-DETR;
   - same 640 input and schedule where possible.
2. **UAV-specific detectors**
   - QueryDet, CEASC, ClusDet, DMNet, UFPMP-Det, TPH-YOLOv5, UAV-DETR, RemDet;
   - reproduced where possible, literature rows labeled.
3. **Ablation and mechanism controls**
   - same detector family;
   - architecture, resolution, exposure, and sampling separated.

### 5.2 Fairness contract

For each comparison record:

- same dataset and split;
- evaluator;
- input size;
- schedule;
- batch and GPU count;
- checkpoint source;
- pretrained or from scratch;
- parameters/FLOPs;
- seed count;
- protocol;
- reproduced or literature;
- deviations.

If full matching is impossible, disclose it and avoid an algorithm-only causal
claim.

## 6. Statistical discipline

1. Key treatment/control: at least five seeds when feasible.
2. Report mean, standard deviation, and n.
3. Prefer paired seed-wise differences.
4. Report confidence intervals for final claims.
5. Do not call a result significant without a test and effect size.
6. Distinguish practical gain from statistical uncertainty.
7. Keep best-checkpoint policy identical across arms.

## 7. Writing order

A reliable order is:

1. Methods;
2. Results;
3. Discussion;
4. Introduction;
5. Abstract and conclusion;
6. Cover letter.

Write the most factual sections first. Generalize only after results stabilize.

### Paragraph function table

| Section | Paragraph function | Allowed inputs |
|---|---|---|
| Intro 1 | UAV detection pathologies | Verified citations and dataset facts |
| Intro 2 | Gap in architecture-first or confounded comparisons | Literature matrix |
| Intro 3 | Contributions and bounded result | Fact table |
| Methods | Reproducible profiler and policy | Code and fact table |
| Results | Main table, ablations, controls | Evaluation JSON |
| Discussion | Mechanism, comparison, limitations | Controlled contrasts |
| Conclusion | Bounded final claim | Evidence matrix |

## 8. Figure quality gates

Every figure must have:

- one clear message per panel;
- consistent terminology;
- the same protocol as the cited table;
- error bars or seed information where relevant;
- vector PDF where possible;
- readable font at final column width;
- no internal run IDs;
- no unexplained abbreviations;
- a caption stating comparison and controls;
- committed plotting script.

Useful DAHP figure set:

1. pathology profile;
2. method pipeline;
3. architecture/resolution ladder;
4. regime matrix;
5. attribution waterfall;
6. online prediction;
7. per-class radar;
8. qualitative results.

## 9. Claim-evidence audit before submission

Create a claim-evidence table and audit abstract, contributions, results,
discussion, and conclusion:

| Manuscript claim | Exact evidence | Protocol | Status |
|---|---|---|---|
| ... | ... | ... | supported / pending / remove |

If a claim has no row, remove it or add the experiment.

## 10. Consistency checks

After every edit:

1. compile twice;
2. no LaTeX errors;
3. no undefined references;
4. no overfull boxes;
5. labels and citations resolve;
6. numbers unchanged unless intentionally updated;
7. terminology consistent;
8. methods equations match code;
9. script defaults match paper;
10. figure data match table data;
11. references verified;
12. supplementary tables referenced;
13. internal run IDs removed;
14. funding, ethics, and data statements reviewed.

## 11. Reusable audit questions

### Fact extraction

- Which source file fixes the dataset, split, model, schedule, evaluator, and hardware?
- Which fields remain unknown and must be marked pending?
- Which values have multiple protocols and therefore require separate columns?

### Claim audit

- Does each factual claim map to a table, figure, equation, or evaluation record?
- Does any claim mix protocols, input sizes, or incomplete evidence?
- Which wording accurately reflects the strength of the evidence?

### Fairness audit

- Are split, input size, epochs, batch, hardware, checkpoint source, evaluator,
  and protocol identical or explicitly disclosed?
- Is the row same-protocol, reproduced, or literature-only?
- Does the comparison avoid attributing resolution or capacity effects to the
  sampling policy?

### Figure audit

- Does each panel communicate one bounded message?
- Are terminology, units, legends, and data sources consistent with the tables?
- Are fonts readable at final column width and is the plotting script available?

### Reference audit

- Are authors, title, venue, year, pages, DOI, and URL complete and verified?
- Does the cited experiment actually support the sentence it is attached to?
- Are validation, test-dev, and challenge results distinguished?

## 12. Reboot-safe server workflow

Practices used in this project:

1. one experiment per GPU;
2. pass `--device N`; do not rely only on `CUDA_VISIBLE_DEVICES`;
3. checkpoint-aware resume for every run;
4. queue scripts check epochs and process state before relaunch;
5. `@reboot` crontab entries launch supervisors;
6. logs in `logs/`, evaluation in `results/eval/`;
7. respect the agreed GPU quota;
8. detect stalls using process age, results-file mtime, and GPU utilization;
9. evaluate completed checkpoints immediately;
10. never insert partial training metrics into the manuscript.

## 13. Submission package checklist

- [ ] main manuscript in journal template;
- [ ] cover letter;
- [ ] highlights;
- [ ] graphical abstract;
- [ ] author contributions;
- [ ] competing interests;
- [ ] data availability;
- [ ] code release;
- [ ] supplementary tables;
- [ ] per-class results;
- [ ] failure/negative-result audit;
- [ ] reference export;
- [ ] figure source scripts;
- [ ] reproducibility instructions;
- [ ] checksums for released result summaries.

## 14. Common pitfalls and fixes

| Pitfall | Fix |
|---|---|
| Language polishing changes a number | Freeze result columns and audit a before/after diff |
| Mixed protocols in one subtraction | Separate md100/native columns |
| Same-epoch exposure confounded with sampling | Add random-volume and exposure-matched controls |
| Resolution and algorithm change together | Use same-input ablation and ladder |
| SOTA claim from heterogeneous literature rows | Say strongest reproduced comparator under protocol |
| Too few seeds but significance wording | Increase n or report descriptive statistics |
| Methods equation differs from code | Verification script and result JSON |
| Discussion repeats introduction | Write discussion after results by mechanism |
| Pretty but unclear figure | Require one message per panel and plotting script |
| Internal run names leak | Map to scientific names before release |

## 15. DAHP case-study sequence

1. Diagnose label-level pathologies: scale, long tail, structural overlap.
2. Reproduce baselines under one evaluator.
3. Run architecture ladder to separate P2, capacity, and resolution.
4. Test sampling families: tail, confusion, union, curated allocator.
5. Add random-volume and exposure-matched controls.
6. Derive the exposure-aware regime principle.
7. Test online prediction with a two-arm probe.
8. Transfer to UAVDT.
9. Add modern baselines and the negative-result audit.
10. Synchronize paper, code, figures, and release artifacts after every result.

This sequence is reusable for other data-centric detection papers.
