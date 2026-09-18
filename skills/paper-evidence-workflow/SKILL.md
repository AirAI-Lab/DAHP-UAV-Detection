---
name: paper-evidence-workflow
description: Plan, implement, revise, and audit evidence-backed research papers and experiment code, including fair baselines, controlled experiments, claim traceability, figures, reproducibility, review response, and submission readiness. Use for manuscript drafting, revision, or research-code workflows; not for unrelated prose editing.
---

# Paper Evidence Workflow

Maintain an unbroken chain from raw experimental records to every manuscript claim. Never let a narrative claim outrun its evidence. The researcher owns hypotheses, interpretations, claims, authorship decisions, and final approval.

## Route to a reference

Read only the reference needed for the current mode:

- **New project or full thesis-to-paper process:** `references/research-lifecycle.md` and `references/research-lifecycle.zh-CN.md`.
- **Research code, queues, checkpoints, servers, release engineering:** `references/experiment-code-ops.md` and `.zh-CN.md`.
- **Working with Codex from idea to submission:** `references/codex-research-collaboration.md` and `.zh-CN.md`.
- **DAHP project history and reusable lessons:** `references/dahp-case-study.md` and `.zh-CN.md`.
- **Ready-to-copy tables and checklists:** `references/artifact-templates.md` and `.zh-CN.md`.

Maintain substantial project documents in English and Chinese. When a result changes, update both language versions in the same commit.

## Required project artifacts

Before substantial writing or implementation, create:

1. **Fact table** — dataset/split, counts, model, checkpoint provenance, hardware, package versions, schedule, batch, seeds, metric definitions, evaluation protocol, latency protocol, completed/pending results, and deviations.
2. **Literature evidence matrix** — verified citation key, exact finding, benchmark/split, input size, protocol, and limitation.
3. **Experiment matrix** — research question, hypothesis, treatment, control, fixed variables, metrics, seed policy, decision rule, and failure mode.
4. **Claim-evidence matrix** — manuscript sentence, evidence file/table/figure, protocol, uncertainty, status, and action.
5. **Run/status board** — active and completed runs, epochs, best/final metrics, process state, result mtime, and intended paper use.
6. **Submission checklist** — manuscript, supplements, cover letter, statements, code, data availability, and reproducibility instructions.

Mark unknown facts `PENDING`; never infer them. Keep incomparable protocols in separate fields.

## Research and experiment design

- State a one-sentence thesis that the full paper must prove.
- Derive research questions from that thesis; every experiment must answer a question or expose a boundary condition.
- Separate architecture, input resolution, capacity, training exposure/data volume, targeted policy, evaluator, and schedule.
- Use a three-tier comparison:
  1. same-protocol general baselines;
  2. domain-specific baselines marked reproduced/literature/official weights;
  3. same-detector ablations and mechanism controls.
- Record split, input size, epochs, batch, hardware, checkpoint provenance, parameters/FLOPs, evaluator, protocol, and deviations for every baseline.
- Add volume-matched and exposure-matched controls when data duplication or schedule changes can explain a gain.
- Report n, mean, standard deviation, and paired differences where available. Avoid significance language without a valid test and effect size.
- Keep checkpoint-selection policy identical across arms.

## Writing and revision sequence

1. Methods — only facts present in the fact table and code.
2. Results — one controlled finding per paragraph; state effects and boundaries.
3. Discussion — mechanism, comparison with prior work, limitations, and scope.
4. Introduction — pathology, gap, bounded contribution, and core result.
5. Abstract and conclusion — reuse only supported claims.
6. Cover letter and supplementary material.

For reviewer comments, create a response matrix: concern, type, manuscript location, evidence needed, change made, limitation, and exact response. Prefer controlled experiments over rhetorical defense.

## Claim and fairness audit

For every factual sentence verify:

- numeric source;
- evaluation protocol;
- split;
- input size;
- schedule and exposure;
- reproduced versus literature status;
- validity of subtraction;
- n and uncertainty;
- whether “state of the art”, “causes”, “significant”, or “architecture-free” is justified.

If a claim has no evidence row, remove it or add the experiment. Pending evidence stays out of final conclusions.

## Figure, table, and code audit

- One message per figure panel; captions state comparison and controls.
- Plot data come from the same result files as tables.
- Terminology, units, abbreviations, class names, and protocol labels are consistent.
- Equations, code defaults, manuscript parameters, and released configs agree.
- Figure/table scripts are committed and fail on missing results.
- Seeds, resume behavior, evaluator, and environment are reproducible.
- Public releases contain no private paths, credentials, internal IDs, or unexplained machine-specific assumptions.

## Final quality gates

- [ ] every abstract and contribution claim has an evidence row;
- [ ] pending items are excluded from final claims;
- [ ] no mixed-protocol subtraction;
- [ ] baseline deviations disclosed;
- [ ] statistical language matches n and tests;
- [ ] equations match implementation;
- [ ] figures and tables match raw results;
- [ ] references verified and correctly scoped;
- [ ] LaTeX compiles twice without errors, unresolved references, or overfull boxes;
- [ ] supplement, code, data statement, and reproducibility instructions are complete;
- [ ] bilingual documentation is synchronized.
