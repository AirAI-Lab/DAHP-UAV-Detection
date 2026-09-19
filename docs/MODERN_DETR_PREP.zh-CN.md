# Modern DETR Baseline 准备记录

快照：2026-09-18。

## 目的

在服务器不能访问 GitHub 的情况下，提前准备 D-FINE 与 RT-DETRv2 baselines。源码和预训练权重已在本机下载并传输到服务器。

## 源版本

| 模型 | 上游 | 版本 | checkpoint |
|---|---|---|---|
| D-FINE-M | `Peterande/D-FINE` | `956d1709314c2c6a4df6f34de232054578a7449f` | `dfine_m_obj2coco.pth` |
| RT-DETRv2-L | `lyuwenyu/RT-DETR` 的 `rtdetrv2_pytorch` 子目录 | `29320b6fd828f8e0987a71426cf2d961b09dfed7` | `rtdetrv2_r50vd_6x_coco_ema.pth` |

服务器位置：

```text
/home/wn/wn/edge_infer_cloud/third_party/visdrone_staging/dfine
/home/wn/wn/edge_infer_cloud/third_party/visdrone_staging/rtdetrv2
/home/wn/wn/edge_infer_cloud/third_party/visdrone_staging/weights
```

## 数据转换

上游训练器使用 COCO JSON，而本项目 VisDrone 为 YOLO 标签。因此新增并运行 `scripts/build_coco_from_yolo.py`：

```text
visdrone_train_coco_dedup.json
  6,471 张图像
  343,200 个标注
  去除 4 个完全重复框

visdrone_val_coco.json
  548 张图像
  38,759 个标注
```

训练 JSON 去除完全重复的 YOLO 行；验证 JSON 保持当前评估约定。

## 协议

两个 baseline 均使用：

```text
输入：640
训练 total batch：8
epochs：100
seed：0
AMP：开启
网络输入：固定 640x640（禁用上游 multi-scale collation）
D-FINE 验证 batch：2
D-FINE GPU：6
RT-DETRv2 GPU：等待 cf_s45 及最终评估释放 GPU4 后使用
```

D-FINE 使用 Objects365+COCO checkpoint tuning。RT-DETRv2 使用官方 COCO EMA checkpoint tuning。类别数不匹配的分类头由各自上游 tuning 逻辑重新初始化。D-FINE 评估使用 batch 2 只是为了在 GPU6 被其他任务占用部分显存时避免 OOM；不改变训练 batch 和优化曝光。

## 已完成冒烟检查

- D-FINE Python/config import：通过。
- RT-DETRv2 Python/config import：通过。
- D-FINE 数据量：6,471 train / 548 val。
- RT-DETRv2 数据量：6,471 train / 548 val。
- D-FINE head 设置后参数量：19.48M。
- RT-DETRv2 head 设置后参数量：42.75M。
- D-FINE checkpoint tuning load：通过。
- RT-DETRv2 checkpoint tuning load：通过。
- 已用 `PResNet.pretrained: False` 禁止 RT-DETRv2 额外下载 backbone。

## D-FINE evaluator 修正

batch-8 validation sanity check 暴露出 COCO category-ID 映射错误。D-FINE
输出 0-based detector labels，而 VisDrone COCO GT 使用 category ID 1--10。
上游 evaluator 未做数据集特定 `label2category` 映射，导致 AP 无效；但框和
类别的轻量诊断指标合理。训练和 loss 不受影响。

`src/solver/det_engine.py` 现在仅在 COCO evaluation 前通过
`data_loader.dataset.label2category` 转换 detector labels；轻量 validator
继续使用 0-based labels。checkpoint 49 结果：

| Evaluator | AP | AP50 | APs |
|---|---:|---:|---:|
| 映射修正前，validation batch 8 | 2.8 | 4.9 | 2.2 |
| 映射修正后，validation batch 8 | 30.2 | 49.1 | 20.2 |

训练已使用修正后的 evaluator 从 epoch 50 恢复。此前的 log AP 仅作为审计
历史，不得写入论文。

## RT-DETRv2 类别映射修正

RT-DETRv2 首次启动后重复出现 device-side index assertion。原因与 D-FINE
相同：COCO category ID 为 1-based，而 detector labels 为 0-based；VisDrone
category ID 10 超出 10-class head 的有效索引。已修复两条路径：

1. `src/data/dataset/coco_dataset.py` 在训练 target 中通过
   `category2label` 映射声明类别。
2. `src/solver/det_engine.py` 仅在 COCO evaluation 前通过
   `label2category` 映射 detector labels。

失败的 epoch-0 run 目录已删除；queue 在非零退出后 backoff 300 秒，并已从
epoch 0 干净重启。重启后的进程没有再出现 category-index assertion。

## 队列

`scripts/queue_dfine_gpu6.sh` 正在运行且已配置 reboot-safe。它在评估 OOM 后从 epoch-0 checkpoint 恢复，当前验证 batch 为 2；COCO 类别映射修正后已从 epoch 50 恢复。`scripts/queue_rtdetrv2_gpu4.sh` 在类别映射修正后已从 epoch 0 重启，并在失败时 backoff。

准备阶段不占用新的 GPU。
