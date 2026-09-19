# Run 状态板

快照时间：2026-09-19 08:29 UTC / 北京时间 16:29。

## 服务器与队列

下列 supervisor 和最终评估 watcher 均已配置重启自动恢复。D-FINE 的
GPU0 重试队列已移除；D-FINE 现在单独运行在 GPU6，total batch 8。GPU0
专门保留给 batch-2 RT-DETR-L 对照。

当前我方任务使用 6 张 GPU：

| GPU | Run | 进度 | 当前 best AP | 状态 |
|---:|---|---:|---:|---|
| 0 | `base_rtdetrl_b2_640` | 39/100 epochs | native 3.804 | 单独运行；预计晚期收敛 |
| 1 | `s960_rand_b2` | 已启动 0/60 | 待定 | 960 exact random-volume 对照 |
| 3 | `cf_s46` | 88/100 | native 38.729 | targeted-union seed 46 |
| 4 | `cf_s45` | 88/100 | native 38.681 | targeted-union seed 45 |
| 5 | `rtdetr_union_640` | 53/100 | native 4.632 | RT-DETR union arm |
| 6 | `base_dfine_m_640` | 50/100 恢复 | ckpt-49 修正后 AP 30.2 | COCO 类别映射已修复；训练 batch 8 |

`s960_base_b2` 已完成 60 epochs；释放的 GPU1 已用于 960 exact
random-volume 对照。GPU2 和 GPU7 属于其他用户。

## 已完成的公平性对照

- exact 1280 base/random/union：md100 34.6296 / 34.7233 / 35.1223；native
  34.6859 / 34.7770 / 35.1772。
- exact 1280 解释：volume +0.0937，targeted residual +0.3990 md100。
- exact 960 batch 匹配 base/union：md100 28.1009/31.9239（+3.8231）；
  native 28.1722/31.9794（+3.8072）；APs +4.1603；tail mean +4.7704。
- 新的 960 random-volume arm 使用同样 12,276 张图曝光、batch 2、
  60 epochs、seed 0；完成后可替代 legacy 77/23 分解，直接分离 volume 与
  targeted reallocation。
- D-FINE COCO category-ID 映射已修复。checkpoint 49 从无效 AP 2.8 修正为
  validation batch 8 下 AP 30.2。
- 论文 attribution table、Fig. 8 和中英文事实/证据文档已回填 exact 1280 triplet。

## 已排队工作

- `queue_rtdetrv2_gpu4.sh` 等待 `cf_s45` 及最终评估释放 GPU4 后，训练
  RT-DETRv2-L：640 px，total batch 8，100 epochs。
- final-evaluation watcher 会在 `cf_s45`、`cf_s46`、`rtdetr_union_640`
  完成后分别评估。

## 预计完成

当前粗略估计：

- `cf_s45` / `cf_s46`：按当前速度约 5--6 小时，另加评估。
- D-FINE-M：从 epoch 50 起约 8--9 小时。
- batch-2 RT-DETR-L base：约 22--24 小时。
- RT-DETR union：视负载约 25--35 小时。

服务器重启和负载变化会使估计顺延。

## 下一步

1. seeds 45/46 完成后，将 1600 targeted 统计从 n=3 更新为 n=5。
2. 960 random-volume 完成后，回填 exact triplet。
3. batch 匹配的 RT-DETR base/union 均完成并用同一 evaluator 评估后，再加入
   cross-family 证据。
4. 将 D-FINE / RT-DETRv2 上游 COCO 日志解析到统一 result schema。
5. 不同协议的数值保持分块；不得用 md100 与 native/md300 直接相减。
