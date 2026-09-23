# biosnap_unseen_drug_hop2_gcn_tokens_150ep — unseen-drug GCN-token 补实验

> BioSNAP canonical-SMILES unseen-drug 的 Full vs GCN atom-token 补对照（GCN-token 侧）。
> 本目录为 **GCN-token** 侧 5-seed 结果（Full 侧见 `stats_input/biosnap_unseen_drug/SGBANDTI/` 或主表）。

## 运行设置
- 数据：BioSNAP unseen_drug（canonical-SMILES 药物互斥）
- 配置：GCN-token（whole-graph GCN atom tokens，无 rooted K-hop 子图），[B,290,128]，参数量约 1,070,342
- 预算：150 epochs；checkpoint = 验证集 AUROC 最优
- seeds：42/52/62/72/82

## 5-seed 结果
| seed | AUROC | AUPRC | best_epoch | 来源 |
|---|---|---|---|---|
| 42 | 0.8706 | 0.8761 | 90 | 本机(4060) |
| 52 | 0.8789 | 0.8863 | 144 | 本机(4060) |
| 62 | 0.8743 | 0.8832 | 143 | 本机(4060) |
| 72 | 0.8787 | 0.8835 | 89 | B机(4090) |
| 82 | 0.8776 | 0.8799 | 120 | B机(4090) |
| **mean±SD** | **0.8760±0.0035** | **0.8818±0.0039** | | |

> seed72/82 由 B机(4090) 跑（unseen_drug 反序段）；本机 seed42/52/62（4060）。seed62 本机与 B机均跑过，取值低者（本机 0.8743）。

## 材料清单
- [x] seed_summary.csv / seed_summary_stats.csv
- [x] 五组 test_y_true.npy / test_y_pred.npy
- [x] 五个 result_metrics.pt + best checkpoint + best_epoch_metrics.txt
- [x] 运行日志：`run_bcombo_B机日志.log`（B机，16.8MB）+ 本机 seed42/52/62 训练日志
- [x] 代码 commit：公开仓库 `08a9dbb`（本目录全部文件均由该提交引入）；训练发生在私有工作仓库 `e77cbcd`（该 commit 不在公开仓库中，仅作来源留痕）
- [x] unseen_drug CSV SHA256（见下）

## unseen_drug CSV SHA256
```
train.csv 08c16381f0059eb857c0ad508ef72298ece8c2a2256e767e1bf40fc443375398
val.csv   0dc3e6bc0c85ff5a296b21808e17014d66cfa686fe2c0790a2f8960f93230011
test.csv  14888e218560947d4919267367e37a3bde502218f3bfe67678c7fa29845026bf
```

## 与 Full 对照（unseen-drug）
Full mean AUROC 0.8794±0.0019、AUPRC 0.8821±0.0026。
Δ（Full−GCN-token）逐 seed：AUROC 4/5 正、mean +0.0033；AUPRC 2/5 正、mean +0.0003。
判定：AUROC 满足 4/5 正，AUPRC 未满足 → 情形 B（small numerical advantage, not conclusive on AUPRC）。
