# 实验代码与运行运维指南

适用于研究代码实现、训练运行、故障诊断和发布前加固。

## 实现原则

1. **实验可执行**：一个配置足以复现一个命名 run。
2. **方法、训练、评估分离**：评估逻辑不能只存在于训练循环内。
3. **保留 provenance**：保存 git commit、配置、环境、seed、checkpoint 和 evaluator 参数。
4. **尽早失败**：训练前验证标签、类别数、图像路径、GPU 绑定、输出目录和 checkpoint 状态。
5. **原始结果不可变**：聚合和绘图只读结果，不修改结果。
6. **队列脚本确定性**：由脚本判断 start、resume、wait 或 stop。
7. **避免隐藏环境效应**：当 wrapper 显式使用 `--device` 时，不能只依赖 `CUDA_VISIBLE_DEVICES`。

## 最小 run manifest

每个 run 记录：

```yaml
run_name:
  method: 方法标识
  dataset: 路径或规范数据集名
  split: train/val
  model: 结构或 checkpoint
  pretrained: true/false
  input_size: 整数
  batch: 整数
  epochs: 整数
  seed: 整数
  gpu: 整数
  evaluator: 脚本与协议
  best_metric: float
  final_metric: float
  checkpoint: 路径
  config_hash: sha256
  code_commit: git commit
  status: running/complete/failed
```

## 队列与重启安全

健壮队列应：

1. 获得单实例锁；
2. 枚举 job 和 GPU；
3. 从 `results.csv` 判断已完成 epoch；
4. 检查进程是否存活；
5. 有 `last.pt` 则恢复；
6. 只启动缺失 run；
7. 将 launch/resume 事件写入日志；
8. 不超过约定的 GPU 配额；
9. 所有任务完成后干净退出；
10. 可通过 reboot hook 恢复。

故障诊断：

| 症状 | 检查 |
|---|---|
| GPU 空闲但进程存活 | dataloader、验证、NFS、CPU 瓶颈 |
| GPU 空闲且进程死亡 | checkpoint resume、OOM、信号、队列循环 |
| results 文件长期不变 | epoch 时长、进程年龄、验证阶段 |
| epoch 数重复 | resume 失败或 run 名错误 |
| 显存接近满 | batch、碎片化、GPU 上第二个进程 |
| loss NaN | 学习率、AMP、标签、类别索引、增强 |

## 环境与数据检查

训练前确认：

- 包版本与事实表一致；
- 图像/标签数量符合预期；
- class ID 在 `[0, nc-1]` 内；
- 除非预期，没有重复标签；
- box 已裁剪并归一化；
- 空标签策略明确；
- train/val 路径没有交换；
- 标签修改后 cache 已失效。

冒烟测试：

1. 小子集训练 1 epoch；
2. 恢复 checkpoint 并确认 epoch index；
3. 评估已知 checkpoint；
4. 与既有记录比较指标；
5. 生成一张表/图。

## 评估纪律

- 所有 arm 使用相同 checkpoint 选择规则。
- maxDets、IoU 阈值、confidence、NMS/WBF、输入尺寸全部显式。
- best 与 final 指标分开。
- 保存 per-class 和面积指标。
- 不混用 native evaluator 与 COCO md100。
- 存储允许时保留 prediction JSON；否则保留 checksum 与摘要。
- latency 测试要有 warmup、固定精度、batch 和足够样本。

## 统计分析

关键比较：

1. 尽量使用相同 seeds 做配对比较；
2. 报告 n、mean、std、min、max；
3. seeds 对齐时计算 paired difference；
4. 选择与 n 和数据依赖关系匹配的检验；
5. 报告效应量和区间；
6. 声明检验是 exploratory 还是 confirmatory；
7. 不把小的描述性差异称为 significant。

## 图表生成

绘图脚本应：

- 读取 JSON/CSV；
- 断言必需列；
- 每个减法只用一个协议；
- 输出 PDF 和必要 PNG 预览；
- 图例不出现内部 run 名；
- 字体、颜色、术语一致；
- 缺失结果时报错，而不是填零。

表格应由结果摘要生成或校验。人工只能改格式，不能改数值。

## 代码审查清单

- [ ] 公式与实现一致；
- [ ] 默认参数与论文一致；
- [ ] class ID/名称与 dataset YAML 一致；
- [ ] seed 显式；
- [ ] device 选择显式；
- [ ] resume 保存 optimizer 和 epoch 状态；
- [ ] evaluator 独立且确定；
- [ ] 输出目录唯一；
- [ ] 无私有路径、凭据、硬编码 checkpoint；
- [ ] 日志足以诊断失败；
- [ ] 测试覆盖 profile、farm、train smoke、resume、eval smoke。

## 发布工程

发布前：

- 删除私有 IP、用户名、密码和内部项目路径；
- 将内部 run ID 改为科学名称；
- 提供最小公开配置；
- 验证 clean clone 可运行；
- 说明数据目录结构；
- 提供环境文件和包版本；
- 提供结果摘要 checksum；
- 大 checkpoint 与论文结果摘要分离；
- 为论文版本打 tag。
