# GNN-CPI — BindingDB random（逐种子结果）

> 来源：`comprare/CPI_prediction-master/output/result/Metrics--bindingdb--*--seed*.txt`（复现自 `github.com/IBM/Interpretable-... (CPI)`）
> 运行：`python run_training.py bindingdb 2 3 10 3 11 3 3 0.001 0.5 10 0.000001 60 bindingdb 42,52,62,72,82`

## ⚠️ 该基线在 BindingDB 上训练极不稳定

| Seed | best epoch | AUROC | AUPRC | F1 | Sens | Spe | Acc |
|---|---|---|---|---|---|---|---|
| 42 | 22 | 0.9494 | 0.9358 | 0.8624 | 0.8583 | 0.9065 | 0.8865 |
| 52 | **2** | 0.6102 | 0.5138 | 0.2856 | 0.1908 | 0.8974 | 0.6048 |
| 62 | 13 | 0.6059 | 0.5131 | 0.4492 | 0.4058 | 0.7166 | 0.5879 |
| 72 | **1** | 0.5000 | 0.4141 | 0.0000 | 0.0000 | 1.0000 | 0.5859 |
| 82 | 4 | 0.6087 | 0.5141 | 0.4491 | 0.4095 | 0.7073 | 0.5840 |
| **mean±std** | — | **0.6548 ± 0.1712** | **0.5782 ± 0.2045** | — | — | — | — |

**5 个种子里只有 seed_42 正常收敛**（AUROC 0.9494）。其余 4 个的 best epoch 分别是 1–13，即训练刚开始就被判为最优，模型基本没有学到东西：
- **seed_72**：`F1=0.0000 / Sens=0.0000 / Spe=1.0000` —— 模型把所有样本都判为负类，AUROC 恰好 **0.5000**（等价于随机猜测）
- seed_52/62/82：AUROC 0.61 左右，F1 0.29–0.45，同样远低于正常水平

因此本行结果的 mean±std **不代表该方法的真实性能**，`std=0.1712` 几乎全部来自"部分种子完全崩溃"这一事实。

> 论文中该行已注明："GNN-CPI showed unstable training on BindingDB, with a large standard deviation across seeds."
> 跨模型比较以 AUROC/AUPRC 为主，且不应据此行对 GNN-CPI 的实际能力下结论。

## 目录内容

- `seed_{42,52,62,72,82}/best_metrics.txt` — 原始训练日志（含所有 epoch 的 val/test 指标、BEST_EPOCH、BEST_VAL_AUPRC、BEST_TEST）
- `seed_summary.csv` — 上面这张表的机器可读版

## 说明

本目录**只有逐种子指标，没有逐样本预测**（原始运行未保存 `test_y_pred.npy`）；如需逐样本，需重新训练该基线。
