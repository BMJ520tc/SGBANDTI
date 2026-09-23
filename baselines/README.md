# Baselines（对比基线复现说明）

> 6 个基线均已适配：**同一去重 canonical 数据、5 种子 42–82、统一指标口径**（标准 F1、阈值=验证集选优）。
> 各基线目录内含其官方代码与文档；本文件说明如何在本仓库数据上复现。
> 数据源：`../data/`（BioSNAP random/unseen_drug/unseen_target + BindingDB random）。使用前将对应 CSV 放入各基线预期目录（见下）。

## 环境

均基于 `sgbandti` 环境（见 `environment.yml`），个别基线需额外依赖：

| 基线 | 额外依赖 |
|---|---|
| MolTrans | `pip install subword-nmt` |
| TransformerCPI | `pip install gensim` |
| 其余 | 无 |

## 各基线数据放置与运行

| 基线 | 数据放置（从 ../data 拷入） | 运行命令 |
|---|---|---|
| **MolTrans** | `dataset/BIOSNAP/random`、`dataset/bindingdb/random` | `python train_bindingdb.py --task biosnap --seeds 42 52 62 72 82` |
| **MGNDTI** | `datasets/biosnap/{random,unseen_drug,unseen_target}`、`datasets/bindingdb/random` | `python main.py --data biosnap --split random --seeds 42,52,62,72,82` |
| **INGNN** | `datasets/biosnap/{random,unseen_drug,unseen_target}`（+ `ESPF/` 词表已内置） | `python main.py`（main.py 内设 dataFolder/seeds） |
| **TransformerCPI** | `dataset/biosnap/random`、`dataset/bindingdb/random` | `python main_glu.py --data biosnap --seeds 42,52,62,72,82` |
| **GNN-CPI** | `dataset/{biosnap,bindingdb}/random` | `python run_training.py biosnap 2 3 10 3 11 3 3 0.001 0.5 10 0.000001 60 <setting> 42,52,62,72,82` |
| **RF** | `dataset/biosnap/random`、`dataset/bindingdb/random` | `python dti_prediction_bio.py biosnap` |

> 注意：各基线数据路径为相对路径，需从其各自目录下运行；冷启动（unseen_drug/unseen_target）对应数据放对应目录即可。
> 各基线结果与逐种子明细见 `../results/`。

## 基线协议表（checkpoint 选择与阈值规则）

> **协议统一性说明**：各基线的 checkpoint 选择与阈值规则**并不完全一致**（见下表），因此跨模型比较以阈值无关的 **AUROC / AUPRC** 为准；阈值依赖指标（F1/Sens/Spe/Acc）不作跨模型排名。SGBANDTI 自身为"验证集 AUROC 选 checkpoint + 验证集 F1 选阈值"。

| 基线 | checkpoint 选择 | 阈值规则 | 依据 |
|---|---|---|---|
| **SGBANDTI** | 验证集 AUROC 最优 | 验证集 F1 最优 | trainer.py: `e* = argmax AUROC_val`, `τ* = argmax F1_val` |
| **MGNDTI** | 验证集 AUROC 最优 | 同 SGBANDTI | trainer.py:77 `if auroc >= best_auroc` |
| **MolTrans** | 每 seed 保存 best model | 验证集 F1 最优阈值 | test.py:99 `thred_optim = thresholds[argmax(f1)]` |
| **INGNN** | 固定规则 | **固定 0.5** | DTI.py:137 `y_pred >= 0.5` |
| **TransformerCPI** | 每 seed best model | 验证集 AUC 最优 | main_glu.py: `best_model_seed_{seed}.pt` |
| **GNN-CPI** | 验证集 AUPRC 最优 | 验证集 AUPRC 最优 | run_training.py:428-458 |
| **RF** | 无（单模型） | 验证集 F1 最优 | dti_prediction_bio.py |

> **风险提示**：INGNN 固定阈值 0.5、MolTrans 用验证集 F1、GNN-CPI 用验证集 AUPRC——三者阈值协议互不相同，这正是主表仅保留 AUROC/AUPRC 的原因。如需严格统一阈值依赖指标，需从各基线逐样本预测用统一脚本重算。
