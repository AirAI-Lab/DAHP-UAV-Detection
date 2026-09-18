# Codex Research Collaboration Guide

Use this reference when a researcher wants to work with Codex from an initial idea through implementation, experiments, writing, review response, and publication preparation. Codex is an engineering and manuscript workflow assistant; the researcher remains the decision maker for hypotheses, scientific interpretation, claims, authorship, and submission.

## Operating model

Use Codex for:

- reading repositories and extracting objective facts;
- designing controlled experiment matrices;
- writing research code, tests, queue scripts, and evaluation scripts;
- debugging failed runs;
- converting result files into tables and figures;
- checking manuscript consistency;
- formatting citations supplied by the author;
- drafting point-by-point review responses;
- maintaining bilingual project documentation;
- preparing reproducible releases.

Do not delegate to Codex:

- the scientific hypothesis;
- choice of claims;
- interpretation of weak evidence;
- reference validity;
- authorship decisions;
- ethical or funding statements;
- final approval of results;
- submission authorization.

## Project kickoff prompt pattern

Provide Codex with:

1. research goal and non-goals;
2. datasets and expected labels;
3. existing repository paths;
4. hardware and quota;
5. baseline and metric;
6. known constraints;
7. target venue;
8. required artifacts;
9. whether code, paper, or both are in scope.

Example structure:

```text
Read <repository> and produce a research plan without modifying files.
Objective: ...
Non-goals: ...
Datasets: ...
Primary baseline and metric: ...
Hardware constraint: ...
Target venue: ...
First deliverables: fact table, experiment matrix, reproducible baseline.
Do not infer missing values; mark them PENDING.
```

Require Codex to report assumptions separately from facts.

## Milestone 1 — Diagnosis and research plan

Expected outputs:

- objective fact table;
- data audit;
- candidate confounders;
- research questions;
- minimal experiment matrix;
- baseline reproduction plan;
- risks and stopping conditions.

Review questions:

- Is the phenomenon measured on the correct unit?
- Are causes separable?
- Which comparisons are fair?
- What result would falsify the working hypothesis?
- What claim is outside the available evidence?

## Milestone 2 — Implementation

Ask for:

- configuration schema;
- training and evaluation entry points;
- smoke tests;
- resume behavior;
- logging and result schema;
- method/code consistency notes;
- public/private path separation.

Recommended request:

```text
Implement <feature> with tests. Preserve the existing evaluation protocol.
Add a run manifest and fail fast on invalid labels or GPUs. Do not change
scientific defaults without reporting the diff and rationale.
```

Review the patch for:

- default arguments;
- device binding;
- seed;
- checkpoint resume;
- class mapping;
- protocol changes;
- hidden dependencies;
- removed logs.

## Milestone 3 — Experiment operations

Give Codex explicit operational authority and limits:

```text
You may use at most <N> GPUs. Jobs must resume from checkpoints. Do not kill
unrelated processes. Record every launch in the queue log. Stop and report if
a run repeats an epoch, OOMs twice, or writes no result for <timeout>.
```

Require a status report containing:

- GPU/process map;
- completed epochs;
- best metric;
- errors;
- ETA;
- next action.

Do not treat partial training metrics as final evidence.

## Milestone 4 — Evidence aggregation

Request an evidence table with:

```text
claim | evidence file | protocol | n | uncertainty | status | action
```

Ask Codex to flag:

- mixed protocols;
- different input sizes;
- missing seeds;
- literature-only comparisons;
- unsupported causal language;
- stale figure/table values;
- pending results.

Require that each abstract and contribution sentence map to a row.

## Milestone 5 — Manuscript development

Provide the fact table, evidence matrix, verified references, target template, and figure scripts. Ask Codex to draft in this order:

1. Methods;
2. Results;
3. Discussion;
4. Introduction;
5. Abstract;
6. Conclusion.

Useful constraints:

```text
Use only values in the supplied evidence files. Do not round or reinterpret.
Mark uncertain text as TODO. Keep Methods factual and Results bounded. Preserve
terminology. Do not upgrade a reproduced comparison to a benchmark SOTA claim.
```

After drafting, request an audit rather than another unstructured rewrite:

```text
List every factual claim and its evidence row. Identify unsupported claims,
mixed protocols, repeated terminology, and paragraphs whose function is unclear.
```

## Milestone 6 — Review response

For each reviewer comment, ask Codex to create:

```text
Reviewer concern:
Manuscript location:
Technical classification:
New evidence required:
Changes made:
Limitation if evidence cannot be added:
Exact response text:
```

Rules:

- restate the concern respectfully;
- separate opinion from technical fact;
- provide a controlled experiment when feasible;
- report negative results honestly;
- avoid promising unavailable test data;
- quote revised manuscript sections;
- update evidence matrices before response text.

## Milestone 7 — Submission and release

Ask Codex to assemble:

- journal LaTeX build;
- clean figure sources;
- supplementary tables;
- cover letter;
- highlights;
- graphical abstract;
- reproducibility instructions;
- code release checklist;
- result checksums;
- bilingual documentation index.

Final human checks:

- every author approves submission;
- references are verified;
- data and code statements are accurate;
- ethics/funding/competing interests are complete;
- result summaries correspond to tables;
- no private information remains.

## Safe collaboration habits

| Risk | Control |
|---|---|
| Unsupported claim | Claim-evidence matrix |
| Mixed protocol | Separate protocol fields |
| Changed result during polishing | Freeze numeric columns and diff |
| Invented citation | Only verified reference input |
| Hidden code change | Require patch summary and tests |
| Run queue runaway | GPU quota, lockfile, timeout |
| Private path leak | Public-release scan |
| Overlong prose | Paragraph function table |
| Discussion repeats intro | Write after Results, organize by mechanism |
| Review response too defensive | Restate concern and provide evidence |

## Reusable status request

```text
Report project status in four sections:
1. Completed evidence;
2. Running/pending experiments;
3. Manuscript synchronization state;
4. Blockers and next actions.
For every number, give protocol and evidence file. Do not generalize from
pending runs.
```

## Documentation policy

Maintain each substantial project document in English and Chinese:

```text
FACT_TABLE.md / FACT_TABLE.zh-CN.md
EXPERIMENTS.md / EXPERIMENTS.zh-CN.md
REVISION_EVIDENCE_MATRIX.md / REVISION_EVIDENCE_MATRIX.zh-CN.md
PAPER_PROCESS_PLAYBOOK.md / PAPER_PROCESS_PLAYBOOK.zh-CN.md
```

Use one canonical result source for both languages. When results change, update both versions in the same commit.
