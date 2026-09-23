# biosnap_random_hop2_gcn_tokens_150ep — SGBANDTI GCN-token 对照（BioSNAP random）

> SGBANDTI 自身数据归档。standard-GCN atom-token 对照（无 rooted K-hop 子图），AUROC 0.9051±0.0043。

## 配置
- GCN-token：whole-graph GCN atom tokens（无 rooted K-hop 子图），[B,290,128]，150 epochs，与 Full 同参数量(~1,070,342)/mask/BAN
- seeds：42/52/62/72/82

## 5-seed 结果
| seed | AUROC | AUPRC | best_epoch |
|---|---|---|---|
| 42 | 0.9016 | 0.9027 | 130 |
| 52 | 0.9046 | 0.9132 | 129 |
| 62 | 0.9066 | 0.9173 | 132 |
| 72 | 0.9117 | 0.9171 | 150 |
| 82 | 0.9010 | 0.9049 | 92 |
| **mean±SD** | **0.9051±0.0043** | **0.9110±0.0068** | |

> 对照 Full（0.9062±0.0019）：gcn-token 略低但统计上可比。

## 材料
- [x] 5 seed 完整：result_metrics.pt + best checkpoint + model_epoch_150 + plots + markdown 表 + 逐样本 npy
- [x] seed_summary.csv / seed_summary_stats.csv
