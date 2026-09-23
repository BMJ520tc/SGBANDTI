# biosnap_unseen_target_hop2_full_150ep — SGBANDTI Full unseen-target（蛋白互斥）

> SGBANDTI 自身结果归档（冷启动 unseen-target，0.6345±0.0182 等）。

## 运行设置
- 数据：BioSNAP unseen_target（exact-protein-sequence 蛋白互斥）
- 配置：Full（rooted K=2 subgraph GNN），150 epochs
- seeds：42/52/62/72/82

## 5-seed 结果（逐样本重算）
| seed | AUROC | AUPRC |
|---|---|---|
| 42 | 0.6567 | 0.6282 |
| 52 | 0.6154 | 0.5861 |
| 62 | 0.6461 | 0.6355 |
| 72 | 0.6167 | 0.5953 |
| 82 | 0.6378 | 0.6170 |
| **mean±SD** | **0.6345±0.0182** | **0.6124±0.0212** |

## 材料清单
- [x] test_y_pred/y_true.npy ×5（stats_input 逐样本）
- [x] seed_summary.csv / seed_summary_stats.csv
- [x] seed42：result_metrics.pt + best checkpoint（best_model_epoch_100.pth）
- [ ] seed 52/62/72/82 的 result_metrics.pt / checkpoint / best_epoch（仅逐样本，同 unseen_drug 情况）

## 数据源
逐样本：`stats_input/biosnap_unseen_target/SGBANDTI/`。seed42 result_metrics：主仓库 `result/biosnap_unseen_target_hop2/seed_42/`。
