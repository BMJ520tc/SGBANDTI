# -*- coding: utf-8 -*-
"""
冻结最终 split（P0-#6）：记录每个 split CSV 的 md5 哈希、git blob 哈希、实体/正负统计与当前 git commit，
输出到数据目录下的 SPLITS_FROZEN.json 与 SPLITS_FROZEN.md，保证数据版本可审计、可复现。

哈希口径：md5 一律按 LF（\n）行尾计算（Windows 工作区为 CRLF，直接按字节算会漂移），
并额外输出 git blob SHA-1（与行尾无关）。

用法（公开仓库布局，数据在 ../data）：
  cd code && python freeze_splits.py
"""
import glob
import hashlib
import json
import os
import subprocess

import pandas as pd

SPLITS = [
    ("bindingdb", "random"),
    ("biosnap", "random"),
    ("biosnap", "unseen_drug"),
    ("biosnap", "unseen_target"),
]


def read_lf(path):
    """按 LF 口径读取内容。

    仓库以 core.autocrlf=true checkout 时，Windows 工作区文件是 CRLF，
    直接对字节算哈希会随平台漂移，故统一规范化为 LF 后再算。
    """
    with open(path, "rb") as f:
        return f.read().replace(b"\r\n", b"\n")


def md5(data):
    return hashlib.md5(data).hexdigest()


def git_blob_sha1(data):
    """git blob SHA-1，与行尾无关，等价于 git rev-parse HEAD:<path>。"""
    header = b"blob " + str(len(data)).encode() + b"\x00"
    return hashlib.sha1(header + data).hexdigest()


def data_root():
    """公开仓库为 ../data（从 code/ 运行）；私有工作目录为 datasets/。"""
    for root in ("../data", "data", "datasets"):
        if os.path.isdir(root):
            return root
    return "datasets"


def git_head():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "N/A"


def main():
    commit = git_head()
    records = {}
    root = data_root()
    for ds, sp in SPLITS:
        d = os.path.join(root, ds, sp)
        if not os.path.isdir(d):
            print(f"跳过（不存在）: {d}")
            continue
        rec = {"hash": {}, "blob": {}, "counts": {}}
        frames = []
        for s in ["train", "val", "test"]:
            p = os.path.join(d, f"{s}.csv")
            if os.path.isfile(p):
                content = read_lf(p)
                rec["hash"][s] = md5(content)
                rec["blob"][s] = git_blob_sha1(content)
                df = pd.read_csv(p)
                frames.append((s, df))
        all_df = pd.concat([f for _, f in frames], ignore_index=True)
        rec["counts"] = {
            "samples": {s: len(f) for s, f in frames},
            "drugs": int(all_df["SMILES"].nunique()),
            "proteins": int(all_df["Protein"].nunique()),
            "positive": int((all_df["Y"] == 1).sum()),
            "negative": int((all_df["Y"] == 0).sum()),
        }
        records[f"{ds}/{sp}"] = rec

    out = {
        "git_commit": commit,
        "hash_algorithm": "md5",
        "hash_normalization": "LF",
        "hash_note": "hash 按 LF(\\n) 行尾口径计算；工作区为 CRLF 时直接对文件算 md5 会不符，"
                     "请先 tr -d '\\r' 或直接比对 blob。",
        "blob_note": "blob 为 git blob SHA-1，与行尾无关，复核：git rev-parse HEAD:<path>",
        "note": "冻结的最终 split；任何数据变化都会导致哈希改变",
        "splits": records,
    }
    with open(os.path.join(root, "SPLITS_FROZEN.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    with open(os.path.join(root, "SPLITS_FROZEN.md"), "w", encoding="utf-8") as f:
        f.write("# SPLITS_FROZEN（最终数据划分冻结记录）\n\n")
        f.write(f"Git commit: `{commit}`\n\n")
        f.write("| 划分 | split 样本数(t/v/te) | 药物 | 蛋白 | 正/负 | md5(train/val/test) | git blob(train/val/test) |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for k, r in records.items():
            c = r["counts"]
            f.write(f"| {k} | {c['samples']['train']}/{c['samples']['val']}/{c['samples']['test']} "
                    f"| {c['drugs']} | {c['proteins']} | {c['positive']}/{c['negative']} "
                    f"| {r['hash']['train'][:8]}/{r['hash']['val'][:8]}/{r['hash']['test'][:8]} "
                    f"| {r['blob']['train'][:8]}/{r['blob']['val'][:8]}/{r['blob']['test'][:8]} |\n")
        f.write("\n## 复核方式\n\n"
                "md5 按 **LF（`\\n`）行尾口径**计算；本仓库以 `core.autocrlf=true` checkout，"
                "Windows 工作区 CSV 为 CRLF，直接对工作区文件算 md5 会不符。\n\n"
                "```bash\n"
                "# 方式一（推荐）：git blob 哈希，与行尾无关\n"
                "git rev-parse HEAD:<data>/<dataset>/<split>/train.csv\n\n"
                "# 方式二：先规范化为 LF，再算 md5\n"
                "tr -d '\\r' < <data>/<dataset>/<split>/train.csv | md5sum\n"
                "```\n")

    print(f"git commit: {commit}")
    for k, r in records.items():
        c = r["counts"]
        print(f"{k}: {c['samples']['train']}/{c['samples']['val']}/{c['samples']['test']} 样本, "
              f"{c['drugs']} 药物, {c['proteins']} 蛋白, 正/负 {c['positive']}/{c['negative']}")
    print(f"已输出 {root}/SPLITS_FROZEN.json 和 {root}/SPLITS_FROZEN.md")


if __name__ == "__main__":
    main()
