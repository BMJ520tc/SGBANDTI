# BioSNAP unseen_drug：Full（rooted K=2）vs GCN atom tokens — 逐 seed 对比

> 该对照用于量化 rooted K-hop 子图的作用。两配置同数据 / 同 150ep / 同种子 / 同 token 形状与参数量，唯一差异 = 是否显式 rooted K-hop 子图。
> Δ = Full − GCN-token。GCN-token seed42/52/62 为本机(4060)、seed72/82 为 B机(4090)。seed62 在 B 机段被重复跑过（0.8807 / 0.8889，未保留产物），本表取留有完整产物的本机那次（0.8743 / 0.8832）；改用 B 机值的敏感性结果见 `run_manifest_gcn_tokens.md` §5。

## 对比表

| seed | Full AUROC | GCN AUROC | ΔAUROC | Full AUPRC | GCN AUPRC | ΔAUPRC |
|---|---|---|---|---|---|---|
| 42 | 0.8801 | 0.8706 | **+0.0094** | 0.8820 | 0.8761 | +0.0059 |
| 52 | 0.8764 | 0.8789 | −0.0025 | 0.8824 | 0.8863 | −0.0039 |
| 62 | 0.8813 | 0.8743 | **+0.0070** | 0.8861 | 0.8832 | +0.0030 |
| 72 | 0.8805 | 0.8787 | +0.0018 | 0.8803 | 0.8835 | −0.0031 |
| 82 | 0.8785 | 0.8776 | +0.0009 | 0.8795 | 0.8799 | −0.0004 |
| **mean±SD** | **0.8794±0.0019** | **0.8760±0.0035** | **+0.0033** | **0.8821±0.0026** | **0.8818±0.0039** | **+0.0003** |

**逐 seed 统计：**
- ΔAUROC 为正方向（Full 优）的 seed：**4/5**（42/62/72/82；仅 52 负）
- ΔAUPRC 为正方向的 seed：**2/5**（42/62；52/72/82 负）
- 样本对齐：两配置同 unseen_drug test（5290），标签一致

## 判定

- AUROC：mean Δ +0.0033、4/5 seed 正 → 满足"多数 seed 为正"
- AUPRC：mean Δ +0.0003、仅 2/5 seed 正 → **未满足**"两项指标均 ≥4/5 seed 正"
- → 结论：unseen-drug 上仅小幅数值优势，AUPRC 证据不足以下定论（small numerical advantage, evidence not conclusive on AUPRC）

**论文中的对应表述**：
> The rooted-subgraph configuration achieved a small numerical advantage under the unseen-drug setting (mean ΔAUROC +0.0033, positive in 4/5 seeds), although the AUPRC evidence was not conclusive.

## 结合 random-pair 结果（跨情形综合）

| 划分 | Full−GCN ΔAUROC | Full−GCN ΔAUPRC | 方向 |
|---|---|---|---|
| random-pair (150ep) | +0.0011 | +0.0022 | Full 略高，3/5 seed 正 |
| random-pair (250ep) | −0.0011 | −0.0018 | GCN 略高 |
| unseen-drug (150ep) | +0.0033 | +0.0003 | Full 略高（AUROC 4/5 正）|

综合：rooted-subgraph 在 random-pair 和 unseen-drug 上均无稳定一致的大幅增益，仅在 unseen-drug AUROC 上呈小幅且不完全一致的数值优势。

## 材料引用
- Full 侧：`per_seed/biosnap_unseen_drug_hop2_full_150ep/`
- GCN-token 侧：`per_seed/biosnap_unseen_drug_hop2_gcn_tokens_150ep/`
