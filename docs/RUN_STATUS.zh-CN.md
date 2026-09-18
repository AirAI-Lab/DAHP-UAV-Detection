# Run 状态板

快照时间：2026-09-18 21:10 UTC / 北京时间 2026-09-19 05:10。

## 服务器与队列

下列 supervisor 和最终评估 watcher 均已配置重启自动恢复。D-FINE 的
GPU0 重试队列已移除；D-FINE 现在单独运行在 GPU6，total batch 8。GPU0
专门保留给 batch-2 RT-DETR-L 对照。

当前我方任务使用 6 张 GPU：

| GPU | Run | 进度 | 当前 best AP | 状态 |
|---:|---|---:|---:|---|
| 0 | `base_rtdetrl_b2_640` | 20/100 epochs | native 2.646 | 单独运行；预计晚期收敛 |
| 1 | `s960_base_b2` | 1/60 | epoch 1 native 0.034 | batch 匹配 960 base |
| 3 | `cf_s46` | 71/100 | native 38.729 | targeted-union seed 46 |
| 4 | `cf_s45` | 71/100 | native 38.681 | targeted-union seed 45 |
| 5 | `rtdetr_union_640` | 44/100 | native 4.632 | RT-DETR union arm |
| 6 | `base_dfine_m_640` | epoch 0 后已恢复 | 待定 | D-FINE-M 训练 batch 8；OOM 后验证 batch 2 |

GPU2 和 GPU7 属于其他用户。

## 已完成的公平性对照

- exact 1280 base/random/union：md100 34.6296 / 34.7233 / 35.1223；native
  34.6859 / 34.7770 / 35.1772。
- exact 1280 解释：volume +0.0937，targeted residual +0.3990 md100。
- 论文 attribution table、Fig. 8 和中英文事实/证据文档已回填 exact 1280 triplet。

## 已排队工作

- `queue_rtdetrv2_gpu4.sh` 等待 `cf_s45` 及最终评估释放 GPU4 后，训练
  RT-DETRv2-L：640 px，total batch 8，100 epochs。
- 960 队列在 60 epochs 后自动评估 `s960_base_b2` 的 md100 与 native/md300。
- final-evaluation watcher 会在 `cf_s45`、`cf_s46`、`rtdetr_union_640`
  完成后分别评估。

## 预计完成

当前粗略估计：

- `s960_base_b2`：按当前 589 秒/epoch 估计约 9--10 小时。
- `cf_s45` / `cf_s46`：约 12--14 小时，另加评估。
- D-FINE-M：若 epoch 0 用时稳定，约 20--24 小时。
- batch-2 RT-DETR-L base：约 30--36 小时。
- RT-DETR union：约 40--46 小时。

服务器重启和负载变化会使估计顺延。

## 下一步

1. 确认 D-FINE 以验证 batch 2 完成 epoch-0 评估，并记录稳定 epoch 用时。
2. seeds 45/46 完成后，将 1600 targeted 统计从 n=3 更新为 n=5。
3. batch 匹配的 RT-DETR base/union 均完成并用同一 evaluator 评估后，再加入
   cross-family 证据。
4. 将 D-FINE / RT-DETRv2 上游 COCO 日志解析到统一 result schema。
5. 不同协议的数值保持分块；不得用 md100 与 native/md300 直接相减。
