# Run 状态板

快照时间：2026-09-19 13:44 UTC / 北京时间 21:44。

## 服务器与队列

服务器在计划重启后已运行 6 小时 14 分钟。所有列出的 supervisor 均自动恢复；
监控的队列日志中没有新的 OOM、traceback 或失败。

当前我方任务使用 5 张 GPU：

| GPU | Run | 进度 | 当前 best AP | 状态 |
|---:|---|---:|---:|---|
| 0 | `base_rtdetrl_b2_640` | 54/100 | native 4.841 | batch-2 RT-DETR-L 对照 |
| 1 | `s960_rand_b2` | 21/60 | native 31.075 | exact random-volume 对照 |
| 4 | `base_rtdetrv2_l_640` | epoch 0 重启 | 待定 | 类别映射已修复；total batch 8 |
| 5 | `rtdetr_union_640` | 61/100 | native 4.907 | RT-DETR union arm |
| 6 | `base_dfine_m_640` | log 89/100 | 修正后 md100 31.532 @ ep86 | COCO 类别映射已修复 |

GPU2、GPU3、GPU7 当前不属于我们的活跃分配。GPU4 上还有其他用户进程，但
RT-DETRv2 的分配仍在披露预算内。

## 上一版状态板之后完成

- `cf_s45`：100/100；native best 38.681。
- `cf_s46`：100/100；native best 38.729。
- 两个 seed 的 md100/native 终评已完成。
- 1600 px targeted union 已达到 n=5：
  - R only：36.548 ± 0.207；
  - random volume：36.906 ± 0.286；
  - targeted union：37.181 ± 0.178。
- 分解：volume +0.358，targeted residual +0.275 AP。这是方向性证据，不作
  显著性声明。
- D-FINE evaluator 已修复 VisDrone category-ID 映射。只有 epoch 51 以后的
  COCO log AP 才有效。
- RT-DETRv2 遇到同类 category-ID 映射问题，在任何有效 epoch 完成前已修复。
  失败的 epoch-0 artifacts 已删除，并干净重启训练。

## 预计完成

- D-FINE-M：剩余 log epochs 约 1--2 小时，另加最终审计。
- `s960_rand_b2`：视负载约 8--11 小时。
- batch-2 RT-DETR-L base：约 17--20 小时。
- RT-DETR union：视负载约 15--22 小时。
- RT-DETRv2-L：刚启动，待 epoch 0--2 稳定后重新估计。

## 下一步

1. 运行 D-FINE 最终 batch-8 validation audit，并把修正后的 COCO 结果解析到
   统一 result schema。
2. `s960_rand_b2` 完成后回填 exact triplet，替代 legacy 77/23 分解。
3. 等待 batch 匹配的 RT-DETR base/union 完成后再做 detector-family claim。
4. 跟踪 RT-DETRv2 早期 epoch，并适配其 evaluator 输出。
5. native/md300 与 md100 分块报告；不得混用协议做减法。
