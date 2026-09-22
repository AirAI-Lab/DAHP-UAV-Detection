# FPS、延迟与显存协议

## 范围

效率测量描述桌面级 GPU 推理，而不是 edge 部署。目标是在同一受控协议下暴露
输入尺寸与 P2 head 的代价。

## 硬件与运行时

| 项目 | 数值 |
|---|---|
| GPU | 1 × NVIDIA GeForce RTX 3090（24 GB），测量期间独占 |
| CPU | 24 cores；运行前后记录 1 分钟负载 |
| 精度 | FP16 |
| Batch | 1 |
| 图像 | 20 张 warm-up，300 张 VisDrone-val 测量图 |
| 同步 | 每张图后 CUDA synchronize |
| 置信度 | 0.25 |

## 测量阶段

`scripts/bench_fps.py` 记录：

1. Ultralytics 报告的预处理时间；
2. 检测器推理时间；
3. 后处理/NMS 时间；
4. 全部测量图的端到端墙钟时间；
5. pipeline residual，定义为端到端时间减去阶段求和；
6. warm-up 后 active/reserved CUDA memory；
7. 参数量与主机负载来源。

只有开始和结束时 GPU 均独占、测量不少于 200 张且所有必需阶段齐全的运行才
可用于论文。共享 GPU smoke test 不是论文测量。

## 命令

```bash
python scripts/bench_fps.py \
  --val-dir data/VisDrone2019/VisDrone2019-DET-val/images \
  --device 0 --warmup 20 --measure 300 --require-exclusive \
  --tags baseline_v8mP2_1280,vanilla_v8l_1600,v8lP2_1600,dahpL_1600 \
  --output results/eval/fps_benchmark_300.json
```

`scripts/validate_fps_result.py` 会在结果进入论文前检查资格。

## 报告结果

最终聚合结果嵌入 `results/eval/paper_results_public.json`。DAHP-L 的端到端
时间为 38.0215 ms / 26.3009 FPS；预处理 7.325 ms、推理 24.405 ms、后处理
1.537 ms、pipeline residual 4.754 ms、CUDA memory 0.348/0.670 GB
（active/reserved）。同结构 YOLOv8l-P2 control 为 39.5982 ms / 25.2537 FPS；
小幅差异不解释为策略加速。主机负载偏高，因此端到端时间偏保守。
