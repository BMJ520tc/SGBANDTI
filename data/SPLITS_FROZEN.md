# SPLITS_FROZEN（最终数据划分冻结记录）

Git commit: `08a9dbb42fe7840267c350da6fd1585cf2d4dbdc`（公开仓库中引入 `data/` 的提交；原始冻结发生于私有工作仓库 `5d93e6c89213c747a6d958a2012885327a03710a`）

| 划分 | split 样本数(t/v/te) | 药物 | 蛋白 | 正/负 | md5(train/val/test) | git blob(train/val/test) |
|---|---|---|---|---|---|---|
| bindingdb/random | 34439/4920/9840 | 14643 | 2623 | 20674/28525 | 5c3f4eed/9d4dafe2/cdcfc9e8 | 07d1907f/f099397a/a8db4635 |
| biosnap/random | 19220/2746/5491 | 4505 | 2181 | 13830/13627 | f5b232de/452f3334/1426fdeb | 4a0bc651/11da782a/07c87ce2 |
| biosnap/unseen_drug | 19372/2795/5290 | 4505 | 2181 | 13830/13627 | b576e0bc/afe9ec28/5af9ddfc | 6f3ed2cc/50c32aed/7c81eae4 |
| biosnap/unseen_target | 19980/2574/4903 | 4505 | 2181 | 13830/13627 | a501bf4d/8fae4532/1e35c17c | 636bc979/cdb7424a/2721ed83 |

## 复核方式

md5 一律按 **LF（`\n`）行尾口径**计算。本仓库以 `core.autocrlf=true` checkout，Windows 工作区 CSV 为 CRLF，**直接对工作区文件算 md5 会不符**。两种正确复核方式：

```bash
# 方式一（推荐）：git blob 哈希，与行尾无关
git rev-parse HEAD:data/biosnap/random/train.csv      # → 4a0bc6514ea2a9da5fe37d7c0f4456b55626e294

# 方式二：先规范化为 LF，再算 md5
tr -d '\r' < data/biosnap/random/train.csv | md5sum   # → f5b232deb97ae36c50fee59117fcd26e
```

## 修正记录

2026-09-23：本文件此前的 md5 **混用了两套行尾口径**（BioSNAP 三项按工作区 CRLF 字节、BindingDB 三项按 LF 计算），直接复核会有半数对不上。现已**全部统一为 LF 口径**，取值与最初冻结时的记录一致；同时补入 `git blob` 哈希列，并把 `git commit` 由不可解析的私有仓库提交改为公开仓库的引入提交。生成脚本 `code/freeze_splits.py` 已同步修正（按 LF 口径计算并输出 blob 哈希），避免再次产生口径漂移。
