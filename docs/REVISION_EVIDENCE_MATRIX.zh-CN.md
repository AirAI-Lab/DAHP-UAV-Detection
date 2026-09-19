# 修订证据矩阵与审计

> 本文档回答：当前证据能否在公平、完整的比较下支持论文科学 claim。`pending` 行不得写成论文最终结论。

## 1. 一句话论点

UAV 检测精度受长尾、尺度与曝光 regime 耦合影响；label-only profile 能识别有效的非侵入训练策略，但 rebalancing 只有在 learnability、exposure headroom 与模型 regime 允许时有效；控制 volume 后，targeted reallocation 只留下较小残差。

## 2. Research-question 证据矩阵

| # | 研究问题 | 已有证据 | 公平控制 | 状态 | 剩余工作 |
|---|---|---|---|---|---|
| RQ1 | 尺度病理是否主导 baseline 行为？ | 85.3% <32 px；640/1280/1600 完整 v8l vs P2 ladder | 同 detector family、同 native/md300 evaluator | **Supported** | 无 |
| RQ2 | 长尾与结构混淆能否仅由标签度量？ | 45:1、23 个高相似类别对、van/truck axis；UAVDT profile | label-only profiler 与论文公式验证 | **Supported** | 保持代码/公式/图一致 |
| RQ3 | rebalancing 效果是否依赖 regime？ | 640/960/1600/1920；exact 960 pair 28.10/31.92 md100；exact 1280 triplet 34.63/34.72/35.12 md100；online probe r=0.983 | exact 960/1280 均匹配 detector、epoch、batch 和 evaluator | **Supported，带 exact controls 单 seed 限制** | 可选复现 exact controls |
| RQ4 | 增益来自曝光还是 targeted sampling？ | exact 960 union +3.82；exact 1280：volume +0.09、targeted +0.40；1600 md100: R 36.55 / random 36.91 / targeted 37.09；1920 exposure-matched control | random-volume 与 120-epoch base control | **Partially supported** | 1600 targeted 完成n=5；exact 960 random 在跑 |
| RQ5 | 原理是否具有预测性？ | 30-epoch two-arm probe，r=0.983，5/5 分离 | 只使用早期 epoch；披露失败 single-arm control | **Supported** | 可选 prospective simulation |
| RQ6 | 策略是否跨数据集迁移？ | UAVDT union +0.69 AP，tail +1.69；frequency-only 无效 | 同 profiler 和策略，不调参 | **Supported** | 无 |
| RQ7 | 策略是否跨 detector family？ | RT-DETR base 完成；union 在跑 | 同 640 / 100 ep | **Pending** | 完成并评估 RT-DETR union |
| RQ8 | 同输入下是否超过 modern general detectors？ | DAHP-M 26.11 vs YOLO26-L 24.90 | 同 val、epoch、evaluator | **当前 YOLO 集合 supported** | D-FINE 在跑；RT-DETRv2 已排队 |
| RQ9 | 是否超过 UAV-specific detectors？ | RemDet repro 29.90；DAHP-L 38.16 | reproduced protocol + compute-matched retrain | **Reproduced protocol 下 supported** | 文献高分辨率值只作上下文 |
| RQ10 | architecture-first 干预是否在此设置中无效？ | 七代 module 与负结果附录 | matched 100ep 与 DFL audit | **限定范围内 supported** | 不外推到未测试 module |
| RQ11 | 推理成本是否如实报告？ | RTX 3090 @1600 24.5 FPS | batch 1、FP16 | **Partially supported** | 增加至少 200 张 latency 分解 |
| RQ12 | benchmark 是否外部完整？ | VisDrone val + UAVDT | dual protocol 与 Rep/Lit 标注 | **Partially supported** | test-dev GT 不可得，明确 validation scope |

## 3. 审稿风险审计

| 审稿 concern | 当前响应 | 证据强度 | 行动 |
|---|---|---|---|
| 论文/代码公式不一致 | 公式、profiler、验证脚本均为 0.6 AR + 0.4 scale | 强 | 发布验证结果 |
| P2 / resolution policy 不一致 | 论文与代码 ladder 一致；architecture ladder 完整 | 强 | 无 |
| 原理属于事后归类 | 改为 principle；加入 online two-arm probe | 强 | 可选 prospective simulation |
| exposure/capacity/learnability 混淆 | 640 learnability、exact 1280 volume/targeted 分解、1920 exposure matching、capacity ladder | 强 | 保持协议分离 |
| SOTA 表述过强 | 删除未公开高分辨率 RemDet claim；使用 strongest reproduced comparator | 强 | 文献行保持分离 |
| modern baselines 缺失 | 加入 YOLO11/12/26 与 RT-DETR-L；D-FINE 在跑且类别映射已修复，RT-DETRv2 已排队 | 中 | 完成并评估两个 DETR baseline |
| seeds 不足 | random n=5；targeted 当前 n=3 | 中 | 两个 targeted seeds 在跑 |
| zero architecture change 含义不清 | policy 不改结构；P2 单独披露和消融 | 强 | 保持精确表述 |
| efficiency 过强 | desktop GPU 表述，不称 edge | 中 | 升级 latency 协议 |
| 负结果不可审计 | appendix audit 与 logs | 强 | 发布 JSON/configs |
| confusion 术语不一致 | annotation-level structural similarity | 强 | 避免 appearance confusion |
| 可复现性 | public code/scripts/manuscript/figures | 中 | 发布 machine-readable summary |

## 4. 理论支持评估

### 已支持机制

1. **Learnability lower bound**：640 px 下 duplication 仅 +0.21 AP，tail 不变。
2. **Volume-driven rescue**：960 px batch 匹配 pair 为 union +3.82 md100 AP，volume 成分主导。
3. **Volume-saturated behavior**：exact 1280 controls 为 base/random/union = 34.63/34.72/35.12 md100 AP；random volume 接近中性，targeted union 保留 +0.40 AP residual。
4. **Intermediate positive-sum window**：1600 px 下 random duplication 与 targeted union 均提升 md100 AP；当前分解为 volume +0.36、targeted +0.18。
5. **Exposure-limited regime**：1920 px same-epoch union +3.83，但 120-epoch base 恢复大部分差距；residual 为 +0.42 md100、+0.92 APs。

### 当前理论判定

| 标准 | 判定 | 原因 |
|---|---|---|
| 理论自洽 | 是 | learnability、exposure headroom、capacity 与受控测量分离 |
| 实验支持 | 大部分 | 五个分辨率均有控制；exact 1280 每 arm 单 seed |
| 预测性 | 是 | online two-arm probe r=0.983 |
| 机制性 | 大部分 | volume/exposure controls 分离原因 |
| 泛化性 | 部分 | 跨数据集成立；跨 detector family pending |

## 5. 公平性审计

### 已匹配维度

| 维度 | 状态 |
|---|---|
| validation split | reproduced rows 使用同一 VisDrone val |
| evaluator | Rep rows 同 evaluator；md100/native 分开 |
| literature values | 明确标注，不与 Rep 值混减 |
| input resolution | DAHP-M@640 与 YOLO11/12/26 存在同输入比较 |
| training schedule | 主 baselines 除披露外均 100 epochs |
| architecture disclosure | P2 与 sampling policy 分离 |
| exposure | 加入 random-volume 与 120-epoch matched control |
| seeds | random n=5；targeted n=3 待 n=5 |
| params/input | 已列出 |
| official weights | RemDet official-weight evaluation 已包含 |

### 已知偏差与必须表述

| 偏差 | 原因 | 必须表述 |
|---|---|---|
| DAHP-L 1600 px，许多 baseline 640 px | resolution 是 policy 一部分 | 不得跨行声称 algorithm-only gain；用 DAHP-M@640 或 ladder |
| RT-DETR 请求 640 但有效训练 1280 | Ultralytics 行为 | footnote 披露 |
| RemDet 1600 retrain 单 GPU compute match | compute control | 已披露 |
| 1920 union 每轮曝光加倍 | exposure 是机制一部分 | 分开报告 same-epoch 与 exposure-matched |
| literature rows 协议不同 | 无法全部复现 | 标注 Lit. 和 split/test-dev |
| test-dev GT 不可得 | benchmark 限制 | 称 validation protocol，不称 official SOTA |

## 6. 完整性清单

### 已完成

- [x] profiler 公式/代码对齐
- [x] 640/960/1280/1600/1920 resolution ladder
- [x] 完整 YOLOv8l vanilla vs P2 ladder
- [x] YOLO11/12/26 modern baselines
- [x] RT-DETR-L base
- [x] RemDet official-weight 与 compute-matched 评估
- [x] UAV-specific literature comparison
- [x] UAVDT transfer
- [x] negative-result appendix
- [x] online regime prediction
- [x] 1920 exposure-matched control
- [x] 5-seed random-volume control
- [x] exact 1280 base/random/union controls
- [x] exact 960 batch 匹配 base/union controls
- [x] 使用 exact 1280 分解重制 Fig. 8
- [x] dual evaluation protocols
- [x] public repository 与 manuscript 同步

### 完整收口前必须完成

- [ ] targeted union n=5
- [ ] RT-DETR union cross-family result
- [ ] n=5 后最终 attribution table
- [ ] machine-readable final evaluation JSON/configs 发布

### 算力允许时强烈建议

- [ ] D-FINE baseline（运行中）
- [ ] RT-DETRv2 baseline（GPU4 排队）
- [ ] expanded FPS protocol
- [ ] prospective online-policy simulation
- [ ] test-dev challenge submission

## 7. 当前允许的 claim 语言

| Claim | 允许？ | 精确表述 |
|---|---|---|
| DAHP-M 在 640 超过 reproduced YOLO26-L | 是 | 同一 validation protocol 下 26.11 vs 24.90 md100 |
| DAHP-L 在我们协议下超过最强 reproduced UAV comparator | 是 | 38.16 vs 29.90 md100，并披露 resolution/capacity policy |
| Union 在 1920 造成 +3.83 | 不能单独这样说 | same-epoch +3.83；exposure-matched residual +0.42 md100 |
| exact 1280 union 超过 random | 可以，但需披露 seed | 单 seed 匹配 triplet 中 random 之上 +0.40 md100 AP |
| Targeted union 显著超过 random | 暂不 | 当前 n=3，方向为 +0.18；等待 n=5 |
| Detector-family independence | 暂不 | RT-DETR union pending |
| Official VisDrone SOTA | 否 | 仅 validation-set protocol |
| Edge real-time | 否 | desktop RTX 3090 real-time |
