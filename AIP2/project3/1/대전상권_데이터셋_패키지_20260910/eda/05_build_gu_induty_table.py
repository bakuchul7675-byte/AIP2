# -*- coding: utf-8 -*-
"""Build the 구x업종-level (n=92) feature table -- higher statistical power."""
import pandas as pd
import os

pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 160)

BASE = r"D:\Desktop\AI Project"
CACHE = os.path.join(BASE, "eda", "cache")

def load(key):
    return pd.read_pickle(os.path.join(CACHE, f"{key}.pkl"))

# ---- base: survival target at 구x업종 (broad category, 19 categories) ----
sv = load("survival_gu_induty").copy()
sv.columns = [c.strip() for c in sv.columns]
sv["target_생존율"] = sv["생존율"].str.rstrip("%").astype(float)
sv["target_폐업율"] = sv["휴폐업율"].str.rstrip("%").astype(float)
tbl = sv[["구", "업종", "총계", "target_생존율", "target_폐업율"]].rename(columns={"총계": "feat_해당업종사업체수_2022"})

print("survival_gu_induty 업종 리스트 (broad, n=19):")
print(sorted(sv["업종"].unique()))

print("\nbiz_status_100 업종 리스트 (100대 생활업종, n=100) -- 카테고리 체계가 다름")
bs = load("biz_status_100").copy()
bs.columns = [c.strip() for c in bs.columns]
print(sorted(bs["업종"].unique())[:20], "...")

print("\nbase_layer 업종대분류 리스트 (n=10):")
bl = load("base_layer").copy()
print(sorted(bl["상권업종대분류명"].unique()))
