# 可复现性

## 发布的数值证据

`results/eval/paper_results_public.json` 是用于审计论文数值的唯一脱敏聚合文件，
包含：

- 40 条评估记录；
- per-class 与 UAVDT 迁移结果；
- 5 种子控制组聚合；
- 复现的现代 baseline；
- 负结果审计；
- 回顾性 early-signal 分析；
- 分阶段延迟与显存测量。

当前聚合文件的 `missing_sources=[]`。SHA-256 校验文件为
`paper_results_public.sha256`：

```bash
sha256sum -c results/eval/paper_results_public.sha256
```

训练 checkpoint、预测 dump、私有路径、GPU UUID 和机器用户名均不发布。若某个
表格数值依赖未发布 artifact，该数值不声称可以仅凭本仓库独立复现。

## 复现 label profile

```bash
python - <<'PY'
from dahp.profiler import DatasetProfiler
profile = DatasetProfiler("configs/visdrone_example.yaml", img_size=1280).profile()
print(profile.imbalance_ratio, profile.small_object_ratio)
print([profile.class_names[c] for c in profile.tail_classes])
print([profile.class_names[c] for c in profile.confusion_axis])
PY
```

请将 YAML 中的 `path`、`train`、`val` 调整为本地数据布局。

## 复现阈值审计

```bash
python scripts/profile_threshold_sensitivity.py \
  --label-dir data/VisDrone2019/VisDrone2019-DET-train/labels \
  --reference-size 1280 \
  --output results/eval/profile_threshold_sensitivity.json
```

发布结果为 `results/eval/profile_threshold_sensitivity.json`；UAVDT 对应文件为
`uavdt_threshold_sensitivity.json`。

## 复现评估与延迟

双 maxDets 评估遵循 `docs/EXPERIMENT_PROTOCOL.md`；300 张图延迟协议遵循
`docs/FPS_PROTOCOL.md`。本仓库不重新分发公开数据集和已训练 checkpoint。

## 环境

可用以下任一方式创建锁定环境：

```bash
conda env create -f environment.yml
```

或在 Python 3.10 环境中安装 `requirements-lock.txt`。
