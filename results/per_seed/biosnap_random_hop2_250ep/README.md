# biosnap_random_hop2_250ep — 250-epoch 训练预算敏感性（SGBANDTI full，BioSNAP random）

> 训练预算敏感性证据：验证 150-epoch 主协议的负结果（rooted-subgraph 无稳定增益）不是单一训练预算的偶然现象。
> 运行日期：2026-09-01。B 机 RTX 4090（seed 52/62/72/82）；seed 42 在本地机器（RTX 4060）。
> 协议与 150-epoch 版完全一致：验证集 AUROC 选最优 epoch（无 early stopping）、验证集选优阈值、cudnn 确定性开启。

## 5-seed 结果

| Seed | 数据来源 | AUROC | AUPRC | best_epoch |
|---|---|---|---|---|
| 42 | `result_metrics.pt`（逐样本未归档） | 0.9105 | 0.9169 | 231 |
| 52 | `test_y_pred/y_true.npy`（逐样本） | 0.9082 | 0.9177 | 231 |
| 62 | `test_y_pred/y_true.npy`（逐样本） | 0.9058 | 0.9117 | 195 |
| 72 | `test_y_pred/y_true.npy`（逐样本） | 0.9142 | 0.9233 | 238 |
| 82 | `test_y_pred/y_true.npy`（逐样本） | 0.9097 | 0.9179 | 240 |
| **mean±std** | | **0.9097±0.0031** | **0.9175±0.0041** | |

> 与 150-epoch 主协议对比（同 5 seed）：AUROC 0.9062±0.0019 → 0.9097±0.0031（+0.0035）；best epoch 从 150ep 的 135–147 后移至 195–240，250-epoch 训练仍在校准后持续有效学习。主协议维持 150 epochs，250-epoch 结果作为训练预算敏感性证据报告。

## 文件说明

- `seed_52/62/72/82/`：B 机（实验室 4090）运行，含逐样本 `test_y_pred.npy`/`test_y_true.npy`（行序 = `data/biosnap/random/test.csv`，5491 行）。
- `seed_42/`：本地（RTX 4060）运行，含 `result_metrics.pt`（完整 test_metrics）与各 epoch markdowntable；**逐样本 npy 未归档**（本地 hypertune 运行未保存逐样本）。

## 来源

- 数值与汇总见 `results/00_实验结果汇总.md`（超参微调表第 5 行）与 `results/01_调参过程与结果.md`。
- B 机 4 seed 逐样本由实验室提供（2026-09-02 拷贝）；本地 seed 42 来自 hypertune 运行 `result/biosnap_random_hop2_tune_maxepoch250/seed_42`。
