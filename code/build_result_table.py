# -*- coding: utf-8 -*-
"""
生成 SGBANDTI 唯一机器可读结果总表（ChatGPT 第一阶段要求）。

每 seed 一行，包含：
  dataset, split, model, configuration, seed,
  test AUROC/AUPRC/F1/Sens/Spe/Acc, best_epoch, validation threshold,
  n_samples, sample_id_range, pred_file, true_file
另输出 per-sample 明细表（sample_id, label, probability, seed）。

用法：
  python build_result_table.py
"""
import glob
import os

import numpy as np
import pandas as pd
import torch

ROOT = os.path.join("..", "data")
RESULT = os.path.join("..", "results", "per_seed")

scenarios = [
    ("biosnap", "random", "full"),
    ("biosnap", "unseen_drug", "full"),
    ("biosnap", "unseen_target", "full"),
    ("bindingdb", "random", "full"),
    ("biosnap", "random", "no_subgraph"),
    ("biosnap", "random", "no_ban"),
    ("biosnap", "random", "no_both"),
]

rows = []
per_sample = []
for data, split, abl in scenarios:
    tag = "" if abl == "full" else f"_{abl}"
    base = os.path.join(RESULT, f"{data}_{split}_hop2{tag}")
    for d in sorted(glob.glob(os.path.join(base, "seed_*"))):
        mp = os.path.join(d, "result_metrics.pt")
        if not os.path.isfile(mp):
            continue
        st = torch.load(mp, map_location="cpu")
        m = st["test_metrics"]
        seed = int(os.path.basename(d).split("_")[1])
        cfg = st.get("config", {})
        cfg_str = str({k: dict(cfg[k]) if hasattr(cfg[k], "keys") else cfg[k] for k in cfg})[:200] if cfg else ""

        row = {
            "dataset": data,
            "split": split,
            "model": "SGBANDTI",
            "configuration": abl,
            "seed": seed,
            "test_auroc": m.get("auroc"),
            "test_auprc": m.get("auprc"),
            "test_f1": m.get("F1"),
            "test_sensitivity": m.get("sensitivity"),
            "test_specificity": m.get("specificity"),
            "test_accuracy": m.get("accuracy"),
            "best_epoch": m.get("best_epoch"),
            "validation_threshold": st.get("best_threshold", m.get("thred_optim")),
            "config": cfg_str,
        }

        # 逐样本关联
        y_pred_f = os.path.join(d, "test_y_pred.npy")
        y_true_f = os.path.join(d, "test_y_true.npy")
        row["pred_file"] = os.path.relpath(y_pred_f) if os.path.exists(y_pred_f) else ""
        row["true_file"] = os.path.relpath(y_true_f) if os.path.exists(y_true_f) else ""
        if os.path.exists(y_pred_f) and os.path.exists(y_true_f):
            yp = np.load(y_pred_f)
            yt = np.load(y_true_f)
            row["n_samples"] = len(yp)
            row["sample_id_range"] = f"[0,{len(yp)-1}]"
            for i in range(len(yp)):
                per_sample.append({
                    "dataset": data, "split": split, "configuration": abl, "seed": seed,
                    "sample_id": i, "label": int(yt[i]), "probability": float(yp[i]),
                })
        else:
            row["n_samples"] = ""
            row["sample_id_range"] = ""
        rows.append(row)

df = pd.DataFrame(rows).sort_values(["dataset", "split", "configuration", "seed"])
out_dir = os.path.join("..", "results")
out = os.path.join(out_dir, "SGBANDTI_result_table.csv")
df.to_csv(out, index=False)
print(f"结果总表已写入 {out}（{len(df)} 行）")

per_df = pd.DataFrame(per_sample)
pout = os.path.join(out_dir, "SGBANDTI_per_sample.csv")
per_df.to_csv(pout, index=False)
print(f"逐样本明细已写入 {pout}（{len(per_df)} 行）")
print("\n总表列：", list(df.columns))
