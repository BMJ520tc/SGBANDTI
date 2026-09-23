# bindingdb_random_hop2_full_150ep — SGBANDTI Full BindingDB random

> SGBANDTI 自身结果归档（主实验 BindingDB，0.9620±0.0010）。

## 配置
- Full（rooted K=2 subgraph GNN），150 epochs
- seeds：42/52/62/72/82

## 5-seed 结果（逐样本重算）
| seed | AUROC | AUPRC |
|---|---|---|
| 42 | 0.9631 | 0.9488 |
| 52 | 0.9610 | 0.9466 |
| 62 | 0.9617 | 0.9468 |
| 72 | 0.9610 | 0.9478 |
| 82 | 0.9629 | 0.9508 |
| **mean±SD** | **0.9620±0.0010** | **0.9482±0.0017** |

## 材料
- [x] test_y_pred/y_true.npy ×5（stats_input）
- [x] seed_summary.csv / seed_summary_stats.csv
- [x] seed42：result_metrics.pt + best checkpoint（best_model_epoch_115.pth）
- [ ] seed 52/62/72/82 result_metrics.pt / checkpoint（仅逐样本）
