# biosnap_unseen_drug_hop2_full_150ep — Full（rooted K=2）unseen-drug 对照基准

> Full（rooted K=2 subgraph）侧 5-seed 基准。GCN-token 侧见同目录 `biosnap_unseen_drug_hop2_gcn_tokens_150ep`。

## 运行设置
- 数据：BioSNAP unseen_drug（canonical-SMILES 药物互斥）
- 配置：Full（rooted K=2 subgraph GNN），[B,290,128]，参数量约 1,070,342
- 预算：150 epochs；checkpoint = 验证集 AUROC 最优
- seeds：42/52/62/72/82

## 5-seed 结果（逐样本统一重算口径）
| seed | AUROC | AUPRC |
|---|---|---|
| 42 | 0.8801 | 0.8820 |
| 52 | 0.8764 | 0.8824 |
| 62 | 0.8813 | 0.8861 |
| 72 | 0.8805 | 0.8803 |
| 82 | 0.8785 | 0.8795 |
| **mean±SD** | **0.8794±0.0019** | **0.8821±0.0026** |

> 5-seed 均值与对照表一致（见 `../unseen_drug_full_vs_gcntoken_对比表.md`），确认逐样本源正确。

## 材料清单
- [x] test_y_pred/y_true.npy ×5（stats_input 逐样本）
- [x] seed_summary.csv / seed_summary_stats.csv
- [x] 五个 result_metrics.pt + best checkpoint + best_epoch_metrics.txt + markdown 表
  - seed42（本机）：best_model_epoch_140.pth
  - seed52/62/72/82（B机完整 result 目录）
- [x] unseen_drug CSV SHA256（与 gcn-token 归档相同数据）

## seed 来源
- seed42：本机(4060)，best_epoch 140
- seed52/62/72/82：B机(4090) 完整 result 目录，best_epoch 145/142/110/113

## 数据源
逐样本来自 `stats_input/biosnap_unseen_drug/SGBANDTI/seed_<s>_{y_pred,y_true}.npy`（主仓库 + 上传包 git）。
seed42 的 result_metrics/checkpoint 来自主仓库 `result/biosnap_unseen_drug_hop2/seed_42/`。

## 与 GCN-token 对照
见 `biosnap_unseen_drug_hop2_gcn_tokens_150ep/README.md` 与 `../unseen_drug_full_vs_gcntoken_对比表.md`。
