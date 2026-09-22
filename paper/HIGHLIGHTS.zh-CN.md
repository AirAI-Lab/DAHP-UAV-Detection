# 论文亮点

1. **Exposure-aware regime-dependent rebalancing principle**：数据级重平衡只有在 learnability 与 data-exposure headroom 允许时有效。Exact controls 显示 960 px 为 volume-dominated，1280 px 为 volume-saturated 且保留 targeted residual，1600 px 为 positive-sum window，1920 px 为 exposure-limited apparent gain。

2. **受控负结果研究**：七代已审计 feature-module 提高验证 DFL，未在本文强 baseline 上提供可靠 AP 改进。

3. **Label-only 画像与有界策略搜索机制**：DAHP 将长尾、尺度与结构混淆统计映射为分辨率/配置和 union-sampling 策略，不修改检测器原生 loss，也不插入推理模块。同一策略无需调参即迁移到 UAVDT。

4. **有边界、协议分离的证据**：在披露的 1600-px/P2 策略下，DAHP-L 在 VisDrone val 达到 38.16 md100 AP / 40.06 native AP。论文单独报告同输入 DAHP-M、modern DETR baselines、负向 matched RT-DETR probe、volume/exposure controls 与 UAVDT transfer，避免过度外推。

5. **完整 latency 审计**：在独占 desktop RTX 3090 上，DAHP-L 的 300 图结果为 end-to-end 38.0 ms / 26.3 FPS，并披露 preprocess、inference、postprocess、pipeline residual、CUDA memory 与 host-load provenance。
