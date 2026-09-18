# End-to-End Research Lifecycle

Use this reference when starting a new research project or reconstructing a project from an idea to a submission-ready paper.

## Stage 0 — Define the research object

Before writing code or prose, record:

1. **Phenomenon**: what failure is being observed?
2. **Unit of analysis**: dataset, image, object class, training run, or deployment case.
3. **Candidate causes**: data distribution, model capacity, optimization, evaluation, protocol, or deployment shift.
4. **Intervention**: what can be changed?
5. **Non-goals**: what will not be claimed?
6. **Success criterion**: quantitative and protocol-specific.

Produce a one-sentence thesis:

```text
We test whether <controlled intervention> improves <task metric> under <protocol>,
while separating <confounding factors>.
```

If this sentence cannot be written, the project is not ready for implementation.

## Stage 1 — Build the objective fact table

Create a fact table before the manuscript. Record only observable facts from code, logs, dataset metadata, and evaluation records.

Minimum fields:

- dataset and version;
- train/validation/test split;
- images and instances per split;
- label taxonomy and class mapping;
- preprocessing and augmentation;
- model, checkpoint provenance, parameter count, and FLOPs;
- optimizer, learning-rate schedule, batch size, epochs, seeds, and GPU count;
- evaluator, metric definitions, maxDets, IoU thresholds, area bins;
- latency protocol;
- completed results;
- pending results;
- deviations from matched budgets.

Use `PENDING` for unknown values. A missing value is safer than an inferred value.

## Stage 2 — Build the literature evidence matrix

Only use citations verified from publisher pages, DOI records, arXiv versions, or curated citation managers. For each paper record:

- exact claim borrowed;
- dataset and split;
- input resolution;
- training budget if reported;
- evaluation protocol;
- whether code or weights are available;
- limitation;
- manuscript section where it will be used.

Separate:

1. reported literature values;
2. reproduced values;
3. official-weight evaluations;
4. challenge/test-server values.

Never subtract numbers across these categories.

## Stage 3 — Design the experiment matrix

For every research question, define:

| Field | Meaning |
|---|---|
| RQ | Question that advances the thesis |
| Hypothesis | Falsifiable statement |
| Treatment | Changed configuration |
| Control | Matched configuration |
| Fixed variables | Everything else held constant |
| Metric | Primary and secondary outcomes |
| Sample size | Seeds or independent runs |
| Decision rule | What result supports or refutes the hypothesis |
| Expected failure | What would invalidate interpretation |

Add experiments only when they close an RQ, expose a boundary condition, or answer a likely reviewer question. Avoid adding methods merely to lengthen a table.

## Stage 4 — Implement reproducibly

Implementation should begin with a run manifest, not a one-off notebook.

Recommended files:

```text
configs/         dataset and experiment configurations
scripts/         build, train, evaluate, aggregate, plot
src/             method implementation
tests/           smoke and consistency tests
docs/            bilingual fact/evidence/process documents
results/         evaluation summaries and manifests
paper/           manuscript sources and figures
```

Rules:

- one experiment has one immutable name and configuration;
- every run writes arguments, checkpoints, metrics, environment, and git commit;
- evaluation is independent of training code;
- random seeds are explicit;
- intermediate metrics never replace final evaluation;
- figures are generated from result files, not manually typed values.

## Stage 5 — Run controlled experiments

Before launch, verify:

- correct GPU binding;
- checkpoint resume;
- schedule and batch;
- dataset YAML;
- class IDs and names;
- evaluator protocol;
- expected checkpoint size;
- disk capacity;
- reboot recovery;
- log location.

During execution, track:

- epochs completed;
- best and last metric;
- process age;
- GPU utilization and memory;
- results-file modification time;
- errors requiring intervention.

A stalled run should be diagnosed from process state and artifacts, not assumed complete.

## Stage 6 — Aggregate evidence

For every completed run, extract:

- primary metric;
- secondary metrics;
- per-class results;
- area-based metrics;
- uncertainty across seeds;
- best epoch;
- final epoch;
- latency and parameter count;
- protocol;
- configuration hash;
- deviations.

Store as JSON or CSV, then generate tables and figures from those files. Keep md100/native, val/test-dev, and best/final values in separate fields.

## Stage 7 — Write the manuscript

Write in this order:

1. Methods;
2. Results;
3. Discussion;
4. Introduction;
5. Abstract;
6. Conclusion;
7. Cover letter.

Methods may contain only facts from the fact table or source code. Results paragraphs should state the controlled comparison, numeric outcome, uncertainty, and boundary. Discussion should interpret mechanisms and limitations, not repeat the introduction.

## Stage 8 — Review and revise

For reviewer comments:

1. restate the technical concern;
2. classify it as method, evidence, statistics, fairness, clarity, or scope;
3. identify the exact manuscript location;
4. decide whether new evidence, rewriting, or a limitation is required;
5. add a claim-evidence row;
6. update the manuscript and supplementary material;
7. compile and cross-check;
8. draft a point-by-point response.

Never answer a methodological concern only with prose if a controlled experiment is feasible.

## Stage 9 — Prepare submission

Submission package:

- journal-template manuscript;
- supplementary tables and figures;
- cover letter;
- highlights;
- graphical abstract;
- author contributions;
- funding statement;
- conflict-of-interest statement;
- data availability statement;
- code release;
- reproduce instructions;
- checksummed result summaries.

Before submission, rerun the claim-evidence audit and LaTeX checks.

## Stage 10 — Post-publication maintenance

Maintain:

- release tag corresponding to the paper;
- frozen result summaries;
- environment file;
- running instructions;
- issue template;
- changelog;
- mapping from manuscript tables to result files.

A paper is complete when another researcher can reproduce the evaluation pipeline and verify each claim without asking for internal files.
