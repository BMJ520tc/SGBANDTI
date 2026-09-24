# DrugBAN 基线证据包

> 背景：DrugBAN 决定两个随机划分中的最高均值，也直接涉及正文中的差值结论；而此前的实验包中没有 DrugBAN 源码版本、配置、五种子原值或预测文件。
> 结论：**上述材料均在本地完整保留，现已直接补入本仓库，DrugBAN 不需要重跑。**
> 整理日期：2026-09-23

## 0. 材料对照

| 待核验项 | 本文位置 |
|---|---|
| 官方代码的准确 commit / release | §1 |
| 本文适配代码或 patch | §2 + `baselines/DrugBAN/patches/drugban_adaptation.patch` |
| 四个实验设置所用 split hash | §3 |
| 种子 42/52/62/72/82 的 AUROC/AUPRC | §4 |
| 验证集模型选择规则 | §5 |
| 逐样本预测或原始日志 | §6 |
| 自动生成均值与 sample SD 的脚本 | §7 |

---

## 1. 上游版本

| 项 | 值 |
|---|---|
| 仓库 | https://github.com/peizhenbai/DrugBAN.git |
| commit | `9923f8c99959e00263103ff9ac61ba0eaccc8e02` |
| date | 2023-02-19（"Add data files"） |
| 论文 | Interpretable bilinear attention network with domain adaptation improves drug–target prediction, *Nature Machine Intelligence* (2022), doi:10.1038/s42256-022-00605-1 |

本仓库 `baselines/DrugBAN/` 即该 commit 的工作副本：除 §2 的两处适配与数据库 CSV 替换（改用本文统一划分，见 §3）外，其余文件与上游逐文件一致。

## 2. 本文适配代码（patch）

文件：**`baselines/DrugBAN/patches/drugban_adaptation.patch`**（277 行；只含 `main.py` 与 `trainer.py`，数据集 CSV 的替换不计入代码 patch）。

复现方式：

```bash
git clone https://github.com/peizhenbai/DrugBAN.git
cd DrugBAN
git checkout 9923f8c99959e00263103ff9ac61ba0eaccc8e02
git apply /path/to/drugban_adaptation.patch
```

> 该 patch 已通过 `git apply --check` 验证可在上游 `9923f8c` 上干净应用。

改动明细：

**`main.py`**
1. 新增 `--seeds`：一次运行多个种子（`--seeds 42,52,62,72,82`），与本文 SGBANDTI 及其余基线的种子协议统一（42/52/62/72/82）。
2. `--split` 的 choices 增加 `unseen_drug` / `unseen_target`（上游仅有 `random` / `cold` / `cluster`），以支持本文的两个冷启动划分。
3. 移除 comet-ml 依赖；输出目录按种子组织，结果直接落盘。

**`trainer.py`**（仅影响阈值依赖指标，**不影响 AUROC/AUPRC**）
4. F1 阈值：上游用 `tpr/(tpr+fpr)` 充当 precision 拼出 F1，改为在 PR 曲线上取标准 `2PR/(P+R)` 的最优阈值，并返回 `f1_score`。
5. 修正 sklearn `confusion_matrix` 布局（`[[TN, FP], [FN, TP]]`）下 sensitivity 与 specificity 互换的写法。

训练配置（`baselines/DrugBAN/configs/DrugBAN.yaml`）：batch size 64、max epoch 100、lr 5e-5、无域适应（`DA.USE: False`，Non_DA / vanilla 配置）。

## 3. 四个实验设置的 split hash

与 SGBANDTI 完全相同的 canonical 去重划分，数据在 `data/`。下表为**git blob 哈希**（`git rev-parse HEAD:<path>`，与工作区行尾无关，可直接复核）：

| 设置 | train / val / test 样本数 | git blob hash（train） | （val） | （test） |
|---|---|---|---|---|
| bindingdb/random | 34439 / 4920 / 9840 | `07d1907f7aada58311126b776381491aabe4f388` | `f099397a181c5ffb68d6c737079355bed1cfe403` | `a8db463509c3e702231c97a7dcec9291c496950e` |
| biosnap/random | 19220 / 2746 / 5491 | `4a0bc6514ea2a9da5fe37d7c0f4456b55626e294` | `11da782a4b533244b12527d8c42eaaa78ae7eb0c` | `07c87ce20136ab93e8e4e2963e2aa40111ec14e0` |
| biosnap/unseen_drug | 19372 / 2795 / 5290 | `6f3ed2cc79ec8ce8a1d86758ac1ff89c1f2a9df7` | `50c32aeda60c206300db9c1ebb455f92af1f1f8d` | `7c81eae4333afa0ffa862c554a64418c25fbb58a` |
| biosnap/unseen_target | 19980 / 2574 / 4903 | `636bc979174ac93e1a9d657076aeee217b7de268` | `cdb7424a6727c036acd88414edd8a8f6bb6522cd` | `2721ed83c22074f860f17df4bf7c85c17a92e3ca` |

复核命令：

```bash
git rev-parse HEAD:data/biosnap/random/train.csv   # → 4a0bc6514ea2a9da5fe37d7c0f4456b55626e294
```

> **行尾说明**：本仓库以 `core.autocrlf=true` checkout，Windows 工作区 CSV 为 CRLF，而 `data/SPLITS_FROZEN.json` 的 md5 按 **LF 口径**计算（2026-09-23 已统一），直接对工作区文件跑 `md5sum` 会不符。故上表一律给出 **git blob 哈希**（`git rev-parse HEAD:<path>`），与行尾无关、可无条件复核。

## 4. 逐种子结果（种子 42/52/62/72/82）

数据源：`results/stats_input/<setting>/DrugBAN/seed_summary.csv`，并附逐样本预测（§6）。全部数值与 `results/results_manifest.csv` 第 37–40 行一致；SD 为 `ddof=1` 的样本标准差。

### 4.1 bindingdb/random

| seed | 42 | 52 | 62 | 72 | 82 | mean ± SD |
|---|---|---|---|---|---|---|
| AUROC | 0.9625 | 0.9619 | 0.9628 | 0.9649 | 0.9638 | **0.9632 ± 0.0012** |
| AUPRC | 0.9518 | 0.9500 | 0.9512 | 0.9548 | 0.9503 | **0.9516 ± 0.0019** |

### 4.2 biosnap/random

| seed | 42 | 52 | 62 | 72 | 82 | mean ± SD |
|---|---|---|---|---|---|---|
| AUROC | 0.9087 | 0.9094 | 0.9078 | 0.9106 | 0.9137 | **0.9100 ± 0.0023** |
| AUPRC | 0.9152 | 0.9137 | 0.9175 | 0.9181 | 0.9217 | **0.9172 ± 0.0031** |

### 4.3 biosnap/unseen_drug

| seed | 42 | 52 | 62 | 72 | 82 | mean ± SD |
|---|---|---|---|---|---|---|
| AUROC | 0.8803 | 0.8722 | 0.8729 | 0.8749 | 0.8748 | **0.8750 ± 0.0032** |
| AUPRC | 0.8874 | 0.8740 | 0.8771 | 0.8820 | 0.8828 | **0.8806 ± 0.0052** |

### 4.4 biosnap/unseen_target

| seed | 42 | 52 | 62 | 72 | 82 | mean ± SD |
|---|---|---|---|---|---|---|
| AUROC | 0.6535 | 0.6817 | 0.6539 | 0.6339 | 0.6570 | **0.6560 ± 0.0170** |
| AUPRC | 0.6326 | 0.6565 | 0.6324 | 0.6147 | 0.6303 | **0.6333 ± 0.0150** |

## 5. 模型选择与阈值规则

- **模型选择**：按**验证集 AUROC 最优**保存 best model（`trainer.py`：`if auroc >= self.best_auroc: …`；并列时取较晚 epoch）。
- **训练预算**：固定 100 epochs，**无 early stopping**。
- **阈值依赖指标**（F1 / Sensitivity / Specificity / Accuracy）：原版在评估时按 PR 曲线最优 F1 取阈值。**本文模型间比较不使用这些指标**，论文排名只用阈值无关的 AUROC / AUPRC，因此本包只归档 AUROC / AUPRC（阈值依赖指标无权威来源，故不列入对比表）。

## 6. 逐样本预测与原始日志

- 逐样本预测（4 设置 × 5 种子，配对 bootstrap 的输入）：
  `results/stats_input/{bindingdb_random,biosnap_random,biosnap_unseen_drug,biosnap_unseen_target}/DrugBAN/seed_{42,52,62,72,82}_y_pred.npy` 与对应 `_y_true.npy`
- 原始训练日志：`baselines/DrugBAN/drugban_bindingdb.log`（BindingDB random）。
- **如实说明**：BioSNAP 三个设置（random / unseen_drug / unseen_target）的 DrugBAN 训练日志未随包保存，现存材料为逐样本预测 + 逐种子汇总。如需原始日志，需要定向补跑。

## 7. 均值与 sample SD 的生成脚本

**`code/build_manifest.py`**：读取 `results/stats_input/<setting>/<model>/seed_*_y_pred.npy` 与 `_y_true.npy`，用 `sklearn.metrics` 重算逐种子 AUROC（`roc_auc_score`）与 AUPRC（`average_precision_score`），再输出 `mean` 与 `x.std(ddof=1)` 的样本标准差，最终生成 `results/results_manifest.csv`（本仓库结果数字的唯一权威来源）。

```bash
conda activate sgbandti
cd code
python build_manifest.py
```

> 该脚本使用的 `average_precision_score` 即 AP 形式的 AUPRC；这与论文 Methods 中的说明一致。

## 8. 已知边界

1. BioSNAP 三个设置的 DrugBAN 训练日志未保留（§6），逐样本预测完整。
2. 本仓库不随包分发 DrugBAN 自带的 `datasets/`；复现时需按 `baselines/README.md` 从 `data/` 拷入对应 CSV。
3. 阈值依赖指标未归档（§5），论文亦未使用。
