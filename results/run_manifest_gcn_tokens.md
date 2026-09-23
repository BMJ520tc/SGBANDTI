# GCN-token 对照运行清单（审稿补充材料）

> 回应审稿意见："实验包已有五种子预测、checkpoint 和模型结构，数值也可核验；但公开源码中没有 `MolecularGCNTokens` 类，训练入口也没有 `gcn_tokens` 选项。"
> 结论：**原始源码已找回并补入公开仓库，本对照不需要重跑**。本文件即为审稿建议中的 run manifest（源码 commit、split hash、五个种子、结果路径）。
> 整理日期：2026-09-23

---

## 1. 源码：已补齐，且确认是当年训练所用的原始实现

### 1.1 类定义与接入点

| 位置 | 内容 |
|---|---|
| `code/gcn.py:157` | `class MolecularGCNTokens(nn.Module)` —— standard-GCN 逐原子 token 编码器（whole-graph，无 rooted K-hop 子图） |
| `code/models.py:38,48-56` | `SGBANDTI.__init__` 读取 `ABLATION.USE_GCN_TOKENS`，为真时以 `MolecularGCNTokens` 作 `drug_extractor` |
| `code/configs.py:29` | `_C.ABLATION.USE_GCN_TOKENS = False`（默认关闭；`# True -> standard GCN atom tokens`） |
| `code/main.py:24,53-57` | CLI `--ablation` choices 含 `gcn_tokens`；`apply_ablation()` 置 `USE_SUBGRAPH=False, USE_GCN_TOKENS=True` |
| `code/test.py:61-76`、`code/eval_with_ci.py:34-64`、`code/aggregate_seeds.py:22` | 评测/汇总入口同样认得 `gcn_tokens` |

补入 commit：**`7f559bf`**（本仓库）。投稿版 commit `08a9dbb` 中确实不存在该类 —— 审稿人的观察对当时的公开快照成立，本清单为补交。

### 1.2 "找回的是原始源码、不是重写"的判据

仓库内 2026-08 训练产物的模型结构归档，与当前 `code/gcn.py` 的类定义逐层一致：

| 归档 `results/per_seed/biosnap_random_hop2_gcn_tokens_150ep/seed_*/model_architecture.txt` | `code/gcn.py` 中的对应实现 |
|---|---|
| `(init_transform): Linear(in_features=75, out_features=128, bias=False)` | `self.init_transform = nn.Linear(in_feats, dim_embedding, bias=False)`（in_feats=75, dim_embedding=128） |
| `(conv_layers): ModuleList((0-2): 3 x GraphConv(in=128, out=128, normalization=both, activation=relu))` | `conv_layers` 依次追加 `num_layers=3` 个 `dglnn.GraphConv(dim_embedding→hidden, activation=F.relu)`（hidden=128） |
| `(lin1): Linear(in_features=384, out_features=128, bias=True)` | `self.lin1 = nn.Linear(num_layers * hidden, hidden)`（3×128=384 → 128） |
| 输出 `[B, 290, 128]` 原子 token + 逐原子真实掩码 | `feats = x.view(B, self.max_nodes, self.output_feats)`；`mask = real_flag.view(B, self.max_nodes)` |

→ 按审稿意见"如果找回原始源码，**不需要重跑**"，本题按源码找回情形处理。

---

## 2. 复现命令

```bash
conda activate sgbandti
cd code

# 1) 建 flat（无子图）缓存
python build_subgraph_cache.py --data biosnap --split random     --hop 2

# 2) GCN-token 对照，5 种子
python main.py --data biosnap --split random --hop 2 \
    --ablation gcn_tokens --seeds 42,52,62,72,82

# 冷启动设置同理
python main.py --data biosnap --split unseen_drug --hop 2 \
    --ablation gcn_tokens --seeds 42,52,62,72,82
```

预算：150 epochs（另有 250-epoch 配置，见 §4.2）；checkpoint 取验证集 AUROC 最优；无 early stopping。

---

## 3. 数据划分（split）与哈希

标准口径为 `data/SPLITS_FROZEN.json`。下表同时给出**git blob 哈希**（`git rev-parse HEAD:<path>`，与工作区行尾无关）与 **LF 规范化 md5**（与冻结记录口径一致）。

| 设置 | 样本数 train/val/test | git blob hash (train / val / test) |
|---|---|---|
| biosnap/random | 19220 / 2746 / 5491 | `4a0bc651…` / `11da782a…` / `07c87ce2…` |
| biosnap/unseen_drug | 19372 / 2795 / 5290 | `6f3ed2cc…` / `50c32aed…` / `7c81eae4…` |

完整 40 位 blob 哈希：

```
biosnap/random     train 4a0bc6514ea2a9da5fe37d7c0f4456b55626e294
                   val   11da782a4b533244b12527d8c42eaaa78ae7eb0c
                   test  07c87ce20136ab93e8e4e2963e2aa40111ec14e0
biosnap/unseen_drug train 6f3ed2cc79ec8ce8a1d86758ac1ff89c1f2a9df7
                    val   50c32aeda60c206300db9c1ebb455f92af1f1f8d
                    test  7c81eae4333afa0ffa862c554a64418c25fbb58a
```

unseen_drug 的 CSV 另有 SHA256 记录，见 `results/per_seed/biosnap_unseen_drug_hop2_gcn_tokens_150ep/README.md`。

> **复核注意（行尾）**：本仓库以 `core.autocrlf=true` checkout，Windows 工作区 CSV 为 CRLF，而 `data/SPLITS_FROZEN.json` 的 md5 按 **LF 口径**计算（2026-09-23 已统一），所以直接对工作区文件跑 `md5sum` 会不符。为避免歧义，本清单一律给出 **git blob 哈希**（`git rev-parse HEAD:<path>`，与行尾无关，即 git 中存储的内容）。

---

## 4. 五种子结果与结果路径

### 4.1 BioSNAP random，150 epochs（论文主对照）

路径：`results/per_seed/biosnap_random_hop2_gcn_tokens_150ep/`

| seed | AUROC | AUPRC | best_epoch |
|---|---|---|---|
| 42 | 0.9016 | 0.9027 | 130 |
| 52 | 0.9046 | 0.9132 | 129 |
| 62 | 0.9066 | 0.9173 | 132 |
| 72 | 0.9117 | 0.9171 | 150 |
| 82 | 0.9010 | 0.9049 | 92 |
| **mean ± sample SD** | **0.9051 ± 0.0043** | **0.9110 ± 0.0068** | |

材料：`seed_*/` 内含 `result_metrics.pt`、best checkpoint、`model_epoch_150.pth`、`model_architecture.txt`、`plots/`、train/valid/test markdown 表、逐样本 `test_y_pred.npy` / `test_y_true.npy`；目录级另有 `seed_summary.csv`、`seed_summary_stats.csv`。

### 4.2 BioSNAP random，250 epochs

路径：`results/per_seed/biosnap_random_hop2_gcn_tokens_250ep/`

| seed | AUROC | AUPRC |
|---|---|---|
| 42 | 0.9141 | 0.9215 |
| 52 | 0.9092 | 0.9202 |
| 62 | 0.9097 | 0.9160 |
| 72 | 0.9104 | 0.9206 |
| 82 | 0.9109 | 0.9184 |
| **mean ± sample SD** | **0.9108 ± 0.0019** | **0.9193 ± 0.0022** |

材料说明：该配置**只有逐样本预测**（`seed_*/test_y_pred.npy` + `test_y_true.npy`），没有 `result_metrics.pt` / checkpoint / markdown 表，因此无法给出 best_epoch 与阈值依赖指标。论文只报告 AUROC/AUPRC（阈值无关），该材料足够支撑表内数值。

### 4.3 BioSNAP unseen_drug，150 epochs（Full vs GCN-token 补对照）

路径：`results/per_seed/biosnap_unseen_drug_hop2_gcn_tokens_150ep/`

| seed | AUROC | AUPRC | best_epoch | 运行机器 |
|---|---|---|---|---|
| 42 | 0.8706 | 0.8761 | 90 | 本机 4060 |
| 52 | 0.8789 | 0.8863 | 144 | 本机 4060 |
| 62 | 0.8743 | 0.8832 | 143 | 本机 4060 |
| 72 | 0.8787 | 0.8835 | 89 | B 机 4090 |
| 82 | 0.8776 | 0.8799 | 120 | B 机 4090 |
| **mean ± sample SD** | **0.8760 ± 0.0035** | **0.8818 ± 0.0039** | | |

材料：`seed_*/` 含 `result_metrics.pt` + best checkpoint + best_epoch 指标 + 逐样本 npy；seed 72/82 来自 B 机包，无 `model_architecture.txt` / markdown 表。运行日志见目录内 `run_bcombo_B机日志.log`。

### 4.4 与 Full 配置的对照

| 设置 | Full | GCN-token | Δ(Full − GCN，均值之差) |
|---|---|---|---|
| biosnap/random 150ep | 0.9062 ± 0.0019 / 0.9132 ± 0.0043 | 0.9051 ± 0.0043 / 0.9110 ± 0.0068 | +0.0011 / +0.0022 |
| biosnap/unseen_drug 150ep | 0.8794 ± 0.0019 / 0.8821 ± 0.0026 | 0.8760 ± 0.0035 / 0.8818 ± 0.0039 | +0.0034 / +0.0003 |

unseen_drug 的逐 seed Δ（其均值 +0.0033 AUROC / +0.0003 AUPRC）与判定（AUROC 4/5 为正、AUPRC 未满足）见 `results/unseen_drug_full_vs_gcntoken_对比表.md`。

### 4.5 数值口径

以上数字与 `results/results_manifest.csv` 第 33、35、36 行逐位一致（该文件是结果数字的唯一权威来源）。SD 为 `ddof=1` 的样本标准差，与本仓库其余表格口径相同。

---

## 5. 需要如实披露的两点

1. **跨机器运行**：unseen_drug 的 seed 72/82 在 B 机（4090）、42/52/62 在本机（4060）运行；seed 62 两台机器都跑过，取数值较低的一方（本机 0.8743）。此披露与 `results/per_seed/biosnap_unseen_drug_hop2_gcn_tokens_150ep/README.md`、`results/unseen_drug_full_vs_gcntoken_对比表.md` 的既有记录一致。
2. **250-epoch 配置缺中间产物**：只有逐样本预测，无 checkpoint / `result_metrics.pt`。若审稿人要求完整训练产物，该配置需要定向重跑（约 5 × 单次训练时长）；150-epoch 主对照不受影响。

## 6. 结论

- 源码（类 + config + 训练入口）已全部补入公开仓库，且经结构逐层比对确认与当年训练所用实现一致；
- split、五种子原值、结果路径、机器来源均已记录在案；
- 按审稿意见，"找回原始源码 → 不需要重跑"。**本控制实验不重跑**。
