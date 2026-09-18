# Artifact 模板

这些模板保持紧凑。复制到项目文档后，只填写已核实字段。

## 1. 事实表

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

## 2. 文献证据矩阵

```markdown
| Claim | Citation key | Evidence type | Dataset/split | Input | Protocol | Limitation | Manuscript use |
|---|---|---|---|---|---|---|---|
```

规则：

- 不使用未核实 citation key；
- 未公开 claim 不作为主证据；
- 协议差异不能藏在同一列中。

## 3. 实验矩阵

```markdown
| RQ | Hypothesis | Treatment | Control | Fixed variables | Metrics | Seeds | Decision rule | Failure mode |
|---|---|---|---|---|---|---|---|---|
```

启动前每行必须回答：

- 隔离了哪个因果因素？
- 什么结果会反驳假设？
- 是否无需额外假设即可解释比较？

## 4. Claim-evidence 矩阵

```csv
claim_id,section,claim,evidence,protocol,n,uncertainty,fairness_control,status,action
```

允许状态：

```text
supported
partially supported
pending
remove
limitation only
```

最终稿的摘要和贡献中不得出现 pending。

## 5. Baseline 公平性合同

```markdown
| Method | Source | Split | Input | Epochs | Batch | GPUs | Checkpoint | Evaluator | Protocol | Deviation | Interpretation limit |
|---|---|---|---|---|---|---|---|---|---|---|---|
```

每行分类为：

```text
same-protocol reproduced
official-weight reproduction
literature-only
compute-matched
protocol-disclosed
```

## 6. 段落功能表

```markdown
| Section | Paragraph | Function | Evidence inputs | Target length | Citation needs |
|---|---|---|---|---|---|
```

常见功能：

- pathology；
- gap；
- method component；
- controlled result；
- mechanism；
- limitation；
- contribution；
- deployment implication。

## 7. 审稿答复矩阵

```markdown
| Reviewer point | Concern type | Location | Evidence needed | Change made | New limitation | Response draft | Status |
|---|---|---|---|---|---|---|---|
```

Concern 类型：

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

## 8. 图审计表

```markdown
| Figure | Message | Data source | Protocol | Comparison | Controls shown | Caption check | Script | Status |
|---|---|---|---|---|---|---|---|---|
```

## 9. Run 状态板

```markdown
| Run | GPU | Epochs | Best | Last | Process | Result mtime | Next action | Paper use |
|---|---:|---:|---:|---:|---|---|---|---|
```

最终评估完成前，不得把 running run 移入 paper use。

## 10. 投稿检查表

```markdown
- [ ] LaTeX 编译两次
- [ ] 无 error、未解析引用、overfull box
- [ ] 摘要每个 claim 有证据
- [ ] pending 结果未进入结论
- [ ] 协议分离
- [ ] 统计表述与 n 一致
- [ ] 图与结果文件一致
- [ ] 公式与代码一致
- [ ] 文献已核实
- [ ] supplement 完整
- [ ] code release 干净
- [ ] data statement 准确
- [ ] cover letter 完整
- [ ] 作者批准完成
```
