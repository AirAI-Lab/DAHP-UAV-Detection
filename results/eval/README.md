# Released result summaries

`paper_results_public.json` is the sanitized numerical-evidence file used by the
manuscript. It contains evaluation metrics, control aggregates, reproduced
modern baselines, the negative-result audit, retrospective early-signal data,
and the final latency/memory audit. It omits predictions, checkpoints, PIDs,
GPU UUIDs, machine-specific paths, and local experiment identifiers.

`profile_threshold_sensitivity.json` and `uavdt_threshold_sensitivity.json`
contain the label-only policy-decision audits. They do not estimate AP.

Raw prediction dumps, checkpoints, and unreleased evaluation artifacts are not
distributed. Run the documented evaluation scripts to regenerate
protocol-compatible inputs.
