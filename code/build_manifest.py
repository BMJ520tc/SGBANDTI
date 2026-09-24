# -*- coding: utf-8 -*-
"""生成 results/results_manifest.csv —— 结果数字的唯一权威清单（P0-2 证据冻结）。

数据来源优先级（全部按仓库根目录相对路径）：
  1) results/stats_input/<setting>/<model>/seed_*_y_{pred,true}.npy   逐样本预测，AUROC/AUPRC 现算
  2) results/per_seed/<dir>/seed_*/<pred,true>.npy                    同上（目录内命名各基线不一）
  3) results/per_seed/<dir>/seed_summary.csv                          仅逐种子（无逐样本）
  4) 00_实验结果汇总.md                                               转录值（逐种子未保存）

存在逐种子的行一律以 5 个种子重算 mean / 样本标准差（ddof=1）；缺任一 seed 即报错退出。

用法：
    python code/build_manifest.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / 'results'
OUT = RESULTS / 'results_manifest.csv'

SEEDS = [42, 52, 62, 72, 82]
# 各基线归档的预测文件名不一致，按优先级取第一个存在的
PRED_NAMES = ['test_y_pred.npy', 'y_prob.npy', 'y_score.npy', 'y_pred.npy']
TRUE_NAMES = ['test_y_true.npy', 'y_true.npy']

COLS = ['dataset', 'split', 'model', 'config', 'auroc_mean', 'auroc_std', 'auprc_mean', 'auprc_std',
        'auroc_s42', 'auroc_s52', 'auroc_s62', 'auroc_s72', 'auroc_s82',
        'auprc_s42', 'auprc_s52', 'auprc_s62', 'auprc_s72', 'auprc_s82',
        'pred_file', 'true_file', 'source']

ROWS = []


def _pick(d, names):
    for n in names:
        p = d / n
        if p.exists():
            return p
    return None


def _per_seed(dirpath, pred_names, true_names):
    """目录下 seed_<s>/ 形式的逐样本预测 -> (auroc[5], auprc[5])；任一 seed 缺失返回 None。"""
    a, p = [], []
    for s in SEEDS:
        sd = dirpath / f'seed_{s}'
        yt = _pick(sd, true_names)
        yp = _pick(sd, pred_names)
        if yt is None or yp is None:
            return None
        y = np.load(yt).ravel()
        z = np.load(yp).ravel()
        a.append(roc_auc_score(y, z))
        p.append(average_precision_score(y, z))
    return np.array(a), np.array(p)


def _per_seed_stats_input(setting, model):
    """results/stats_input/<setting>/<model>/ 下 seed_<s>_y_{pred,true}.npy 形式。"""
    d = RESULTS / 'stats_input' / setting / model
    a, p = [], []
    for s in SEEDS:
        yt, yp = d / f'seed_{s}_y_true.npy', d / f'seed_{s}_y_pred.npy'
        if not (yt.exists() and yp.exists()):
            return None
        y = np.load(yt).ravel()
        z = np.load(yp).ravel()
        a.append(roc_auc_score(y, z))
        p.append(average_precision_score(y, z))
    return np.array(a), np.array(p)


def _per_seed_summary(dirpath):
    """results/per_seed/<dir>/seed_summary.csv（只有逐种子 AUROC/AUPRC，无逐样本）。"""
    f = dirpath / 'seed_summary.csv'
    if not f.exists():
        return None
    t = pd.read_csv(f).set_index('seed')
    if not set(SEEDS).issubset(set(t.index)):
        return None
    return (t.loc[SEEDS, 'AUROC'].to_numpy(float),
            t.loc[SEEDS, 'AUPRC'].to_numpy(float))


def add(dataset, split, model, config, per_seed, pred_file='', true_file='', source=''):
    """per_seed = (auroc[5], auprc[5]) 或 None（None 表示无逐种子，由调用方随后填 mean±SD）。"""
    row = dict.fromkeys(COLS, '')
    row.update(dataset=dataset, split=split, model=model, config=config)
    if per_seed is not None:
        a, p = per_seed
        if len(a) != len(SEEDS):
            sys.exit(f'错误：{dataset}/{split}/{model}/{config} 只有 {len(a)} 个种子，需要 {len(SEEDS)} 个')
        row['auroc_mean'], row['auroc_std'] = round(a.mean(), 4), round(a.std(ddof=1), 4)
        row['auprc_mean'], row['auprc_std'] = round(p.mean(), 4), round(p.std(ddof=1), 4)
        for i, s in enumerate(SEEDS):
            row[f'auroc_s{s}'], row[f'auprc_s{s}'] = round(float(a[i]), 4), round(float(p[i]), 4)
    row['pred_file'], row['true_file'], row['source'] = pred_file, true_file, source
    ROWS.append(row)
    return row


def add_transcribed(dataset, split, model, auroc_mean, auroc_std, auprc_mean, auprc_std):
    """逐种子未保存的行：mean±SD 转录自 00_实验结果汇总.md。"""
    row = add(dataset, split, model, 'full', None,
              source='00_实验结果汇总.md（mean±sample SD，ddof=1；逐 seed 未公开归档）')
    row.update(auroc_mean=auroc_mean, auroc_std=auroc_std, auprc_mean=auprc_mean, auprc_std=auprc_std)


def add_stats_input(dataset, split, setting, model='SGBANDTI'):
    d = f'results/stats_input/{setting}/{model}'
    add(dataset, split, model, 'full', _per_seed_stats_input(setting, model),
        pred_file=d + '/', true_file=d + '/',
        source=f'{d}/seed_*_y_pred.npy（逐样本重算）')


def add_per_seed(dataset, split, model, config, dirname):
    d = f'results/per_seed/{dirname}'
    a = _per_seed(RESULTS / 'per_seed' / dirname, PRED_NAMES, TRUE_NAMES)
    if a is not None:
        add(dataset, split, model, config, a, pred_file=d + '/', true_file=d + '/',
            source=f'{d}/seed_*/test_y_pred.npy（逐样本重算）')
        return
    a = _per_seed_summary(RESULTS / 'per_seed' / dirname)
    if a is not None:
        add(dataset, split, model, config, a, pred_file=d + '/', true_file=d + '/',
            source=f'{d}/seed_summary.csv（逐 seed 归档，无逐样本）')
        return
    sys.exit(f'错误：{d} 下既无逐样本预测也无完整的 seed_summary.csv')


# ---- 1) SGBANDTI 四个划分（results/stats_input/） ----
add_stats_input('biosnap', 'random', 'biosnap_random')
add_stats_input('bindingdb', 'random', 'bindingdb_random')
add_stats_input('biosnap', 'unseen_drug', 'biosnap_unseen_drug')
add_stats_input('biosnap', 'unseen_target', 'biosnap_unseen_target')

# ---- 2) SGBANDTI 消融（biosnap random） ----
add_per_seed('biosnap', 'random', 'SGBANDTI', 'no_subgraph', 'biosnap_random_hop2_no_subgraph')
add_per_seed('biosnap', 'random', 'SGBANDTI', 'no_ban', 'biosnap_random_hop2_no_ban')
add_per_seed('biosnap', 'random', 'SGBANDTI', 'no_both', 'biosnap_random_hop2_no_both')

# ---- 3) 基线：BioSNAP random ----
add_per_seed('biosnap', 'random', 'MGNDTI', 'full', 'MGNDTI_biosnap_random')
add_transcribed('biosnap', 'random', 'MolTrans', 0.8867, 0.0050, 0.8927, 0.0053)
add_transcribed('biosnap', 'random', 'INGNN', 0.8722, 0.0006, 0.8776, 0.0013)
add_transcribed('biosnap', 'random', 'TransformerCPI', 0.8399, 0.0068, 0.8553, 0.0048)
add_per_seed('biosnap', 'random', 'RF', 'full', 'RF_biosnap_random')
add_transcribed('biosnap', 'random', 'GNN-CPI', 0.7094, 0.0032, 0.7247, 0.0019)

# ---- 4) 基线：BindingDB random ----
add_per_seed('bindingdb', 'random', 'MGNDTI', 'full', 'MGNDTI_bindingdb')
add_per_seed('bindingdb', 'random', 'RF', 'full', 'RF_bindingdb')
add_per_seed('bindingdb', 'random', 'MolTrans', 'full', 'MolTrans_bindingdb')
add_transcribed('bindingdb', 'random', 'INGNN', 0.9228, 0.0028, 0.8951, 0.0024)
add_per_seed('bindingdb', 'random', 'TransformerCPI', 'full', 'TransformerCPI_bindingdb')
add_per_seed('bindingdb', 'random', 'GNN-CPI', 'full', 'GNN-CPI_bindingdb')

# ---- 5) 基线：BioSNAP unseen_drug ----
add_per_seed('biosnap', 'unseen_drug', 'MGNDTI', 'full', 'MGNDTI_biosnap_unseen_drug')
add_per_seed('biosnap', 'unseen_drug', 'RF', 'full', 'RF_biosnap_unseen_drug')
add_transcribed('biosnap', 'unseen_drug', 'TransformerCPI', 0.8460, 0.0113, 0.8551, 0.0061)
add_transcribed('biosnap', 'unseen_drug', 'INGNN', 0.8417, 0.0057, 0.8510, 0.0023)
add_per_seed('biosnap', 'unseen_drug', 'MolTrans', 'full', 'MolTrans_biosnap_unseen_drug')
add_transcribed('biosnap', 'unseen_drug', 'GNN-CPI', 0.6797, 0.0897, 0.6795, 0.0933)

# ---- 6) 基线：BioSNAP unseen_target ----
add_per_seed('biosnap', 'unseen_target', 'RF', 'full', 'RF_biosnap_unseen_target')
add_per_seed('biosnap', 'unseen_target', 'MGNDTI', 'full', 'MGNDTI_biosnap_unseen_target')
add_transcribed('biosnap', 'unseen_target', 'MolTrans', 0.6820, 0.0166, 0.6788, 0.0193)
add_transcribed('biosnap', 'unseen_target', 'INGNN', 0.6526, 0.0090, 0.6421, 0.0075)
add_transcribed('biosnap', 'unseen_target', 'GNN-CPI', 0.6501, 0.0030, 0.6526, 0.0017)
add_transcribed('biosnap', 'unseen_target', 'TransformerCPI', 0.6160, 0.0319, 0.6032, 0.0216)

# ---- 7) SGBANDTI atom-token 对照与长训练配置 ----
add_per_seed('biosnap', 'random', 'SGBANDTI', 'gcn_tokens', 'biosnap_random_hop2_gcn_tokens_150ep')
add_per_seed('biosnap', 'random', 'SGBANDTI', '250ep', 'biosnap_random_hop2_250ep')
add_per_seed('biosnap', 'unseen_drug', 'SGBANDTI', 'gcn_tokens',
             'biosnap_unseen_drug_hop2_gcn_tokens_150ep')
add_per_seed('biosnap', 'random', 'SGBANDTI', 'gcn_tokens_250ep',
             'biosnap_random_hop2_gcn_tokens_250ep')

# ---- 8) DrugBAN 四个划分 ----
add_stats_input('biosnap', 'random', 'biosnap_random', 'DrugBAN')
add_stats_input('bindingdb', 'random', 'bindingdb_random', 'DrugBAN')
add_stats_input('biosnap', 'unseen_drug', 'biosnap_unseen_drug', 'DrugBAN')
add_stats_input('biosnap', 'unseen_target', 'biosnap_unseen_target', 'DrugBAN')

df = pd.DataFrame(ROWS, columns=COLS).round(4)
missing = df['source'].eq('').sum()
if missing:
    sys.exit(f'错误：{missing} 行缺少来源标注')
df.to_csv(OUT, index=False, encoding='utf-8')
print(f'written: {OUT.relative_to(REPO)}  rows: {len(df)}')
