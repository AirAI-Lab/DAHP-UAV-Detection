# Artifact Templates

These templates are intentionally compact. Copy them into project documentation and fill only verified fields.

## 1. Fact table

```markdown
# Project Fact Table

## Dataset and split

| Item | Fact | Source file | Status |
|---|---|---|---|
| Dataset/version |  |  | fixed/PENDING |
| Train images/instances |  |  |  |
| Validation images/instances |  |  |  |
| Test images/instances |  |  |  |
| Class taxonomy |  |  |  |
| Preprocessing |  |  |  |

## Training protocol

| Item | Fact | Source file | Status |
|---|---|---|---|
| Model |  |  |  |
| Checkpoint provenance |  |  |  |
| Input size |  |  |  |
| Batch |  |  |  |
| Epochs |  |  |  |
| Optimizer/LR |  |  |  |
| Seeds |  |  |  |
| GPUs |  |  |  |

## Evaluation

| Item | Fact | Source file | Status |
|---|---|---|---|
| Metric definition |  |  |  |
| maxDets/IoU/areas |  |  |  |
| Checkpoint selection |  |  |  |
| Latency protocol |  |  |  |

## Results

| Run | Protocol | AP | AP50 | APs | n | Uncertainty | Evidence JSON | Status |
|---|---|---:|---:|---:|---:|---:|---|---|
```

## 2. Literature evidence matrix

```markdown
| Claim | Citation key | Evidence type | Dataset/split | Input | Protocol | Limitation | Manuscript use |
|---|---|---|---|---|---|---|---|
```

Rules:

- no unverified citation key;
- no unpublished claim as primary evidence;
- no protocol mismatch hidden in a shared column.

## 3. Experiment matrix

```markdown
| RQ | Hypothesis | Treatment | Control | Fixed variables | Metrics | Seeds | Decision rule | Failure mode |
|---|---|---|---|---|---|---|---|---|
```

Before launch, every row must answer:

- what causal factor does it isolate?
- what result refutes the hypothesis?
- can the comparison be interpreted without an extra assumption?

## 4. Claim-evidence matrix

```csv
claim_id,section,claim,evidence,protocol,n,uncertainty,fairness_control,status,action
```

Allowed status:

```text
supported
partially supported
pending
remove
limitation only
```

A final manuscript should contain no pending row in the abstract or contributions.

## 5. Baseline fairness contract

```markdown
| Method | Source | Split | Input | Epochs | Batch | GPUs | Checkpoint | Evaluator | Protocol | Deviation | Interpretation limit |
|---|---|---|---|---|---|---|---|---|---|---|---|
```

Classify every row as:

```text
same-protocol reproduced
official-weight reproduction
literature-only
compute-matched
protocol-disclosed
```

## 6. Paragraph function table

```markdown
| Section | Paragraph | Function | Evidence inputs | Target length | Citation needs |
|---|---|---|---|---|---|
```

Typical functions:

- pathology;
- gap;
- method component;
- controlled result;
- mechanism;
- limitation;
- contribution;
- deployment implication.

## 7. Review-response matrix

```markdown
| Reviewer point | Concern type | Location | Evidence needed | Change made | New limitation | Response draft | Status |
|---|---|---|---|---|---|---|---|
```

Concern types:

```text
method
evidence
statistics
fairness
clarity
scope
reproducibility
ethics/data
```

## 8. Figure audit table

```markdown
| Figure | Message | Data source | Protocol | Comparison | Controls shown | Caption check | Script | Status |
|---|---|---|---|---|---|---|---|---|
```

## 9. Run status board

```markdown
| Run | GPU | Epochs | Best | Last | Process | Result mtime | Next action | Paper use |
|---|---:|---:|---:|---:|---|---|---|---|
```

Do not move a run from `running` to `paper use` until final evaluation completes.

## 10. Submission checklist

```markdown
- [ ] LaTeX compiles twice
- [ ] No errors, unresolved references, or overfull boxes
- [ ] Every abstract claim has evidence
- [ ] All pending results excluded
- [ ] Protocols separated
- [ ] Statistics match n
- [ ] Figures match result files
- [ ] Equations match code
- [ ] References verified
- [ ] Supplement complete
- [ ] Code release clean
- [ ] Data statement accurate
- [ ] Cover letter complete
- [ ] Author approvals complete
```
