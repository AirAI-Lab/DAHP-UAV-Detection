---
name: paper-evidence-workflow
description: Plan, revise, and audit evidence-backed research papers, including fair baseline comparisons, controlled experiments, claim-evidence traceability, figures, reproducibility, and submission readiness. Use for manuscript drafting or revision; do not use for unrelated prose editing.
---

# Paper Evidence Workflow

Maintain an unbroken chain from raw experimental records to every manuscript claim. Never let a narrative claim outrun its evidence.

## Required working artifacts

Create these before substantial writing or revision:

1. **Fact table** — dataset/split, counts, model, checkpoint provenance, hardware, package versions, schedule, batch, seeds, metric definitions, evaluation protocol, latency protocol, completed results, pending results, and disclosed deviations.
2. **Literature evidence matrix** — verified citation key, exact finding, benchmark/split, input size, protocol, and limitation. Entries without a verified source are forbidden.
3. **Experiment matrix** — research question, hypothesis, treatment, control, fixed variables, metrics, seed policy, and decision rule.
4. **Claim-evidence matrix** — manuscript sentence, supporting table/figure/JSON/citation, protocol, status (`supported`, `pending`, `remove`), and remaining action.
5. **Submission checklist** — manuscript, cover letter, highlights, graphical abstract, ethics/funding/data statements, supplements, code, and reproducibility instructions.

Mark unknown facts `PENDING`; never infer them. Keep separate columns for incomparable protocols.

## Research and experiment design

- State a one-sentence thesis that the full paper must prove.
- Derive research questions from that thesis; every experiment must answer a question or expose a boundary condition.
- Separate factors that can cause the outcome: architecture, input resolution, capacity, training exposure/data volume, targeted policy, evaluator, and schedule.
- Prefer a three-tier comparison:
  1. same-protocol general baselines;
  2. domain-specific baselines, clearly marked reproduced versus literature;
  3. same-detector ablations and mechanism controls.
- For each baseline, record split, input size, epochs, batch, hardware, checkpoint provenance, parameters/FLOPs, evaluator, protocol, and deviations.
- Use volume-matched and exposure-matched controls when data duplication or schedule changes can explain a gain.
- Report n, mean, standard deviation, and paired differences where available. Avoid significance language without an appropriate test and effect size.
- Keep best-checkpoint selection identical across arms.

## Writing and revision sequence

1. Methods — only facts present in the fact table and code.
2. Results — one controlled finding per paragraph or table; state effects and boundaries without generalizing.
3. Discussion — mechanism, comparison with prior work, limitations, and scope.
4. Introduction — pathology, gap, bounded contribution, and core result.
5. Abstract and conclusion — reuse only claims already supported by the evidence matrix.
6. Cover letter and supplementary material.

Do not repeat the introduction in the discussion. Organize discussion by mechanism and evidence boundaries.

## Claim and fairness audit

For every factual sentence, verify:

- the exact numeric source;
- evaluation protocol;
- train/validation/test split;
- input size;
- schedule and exposure;
- whether the row is reproduced, official-weight reproduction, or literature-only;
- whether subtraction is mathematically and protocol valid;
- whether n and uncertainty are adequate;
- whether wording such as “state of the art”, “causes”, “significant”, or “architecture-free” is justified.

If a claim has no evidence row, either remove the claim or add the required experiment. If an experiment is pending, label it pending internally and keep it out of final conclusions.

## Figure and table audit

- One message per figure panel.
- Caption states the comparison and controls.
- Plot data must come from the same source as the corresponding table.
- Keep units, terminology, abbreviations, class names, and protocol labels consistent.
- Use readable fonts at final column width and preserve vector output where possible.
- Show uncertainty when multiple seeds exist.
- Commit plotting scripts and raw result summaries.

## Code and reproducibility

Before submission or public release:

- verify that method equations, code defaults, and manuscript parameters agree;
- include configs, seeds, evaluation scripts, run manifest, and checksums;
- strip internal run IDs, private paths, credentials, and machine-specific assumptions;
- provide exact environment setup and inference commands;
- document unavailable external ground truth or benchmark limitations;
- separate validation results from official test/challenge claims.

## Final quality gates

Run these checks before calling a manuscript complete:

- [ ] every abstract and contribution claim has an evidence row;
- [ ] all pending items are excluded from final claims;
- [ ] no protocols are mixed in one subtraction;
- [ ] baselines and deviations are disclosed;
- [ ] statistical language matches n and test status;
- [ ] equations match implementation;
- [ ] figures match tables and raw results;
- [ ] references are verified and correctly scoped;
- [ ] LaTeX compiles twice without errors, unresolved references, or overfull boxes;
- [ ] supplement, code, data statement, and reproducibility instructions are complete.
