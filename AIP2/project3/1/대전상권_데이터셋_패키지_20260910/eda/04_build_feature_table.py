# -*- coding: utf-8 -*-
"""Build the 구-level (5-row) feature table from the datasets already vetted."""
import pandas as pd
import os

pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 160)

BASE = r"D:\Desktop\AI Project"
CACHE = os.path.join(BASE, "eda", "cache")

def load(key):
    return pd.read_pickle(os.path.join(CACHE, f"{key}.pkl"))

GU = ["동구", "중구", "서구", "유성구", "대덕구"]
feat = pd.DataFrame({"구": GU}).set_index("구")

# ---- TARGET: weighted survival / closure rate (2020 cohort -> 2022-09) ----
sv = load("survival_gu_induty").copy()
sv.columns = [c.strip() for c in sv.columns]
sv_gu = sv.groupby("구").apply(
    lambda d: pd.Series({
        "target_생존율": (d["현재_22년9월 기준영업중"].sum() / d["총계"].sum() * 100),
        "target_폐업율": (d["현재_22년9월 기준 폐업자"].sum() / d["총계"].sum() * 100),
    }), include_groups=False
)
feat = feat.join(sv_gu)

# ---- FEATURE: recent YoY / MoM momentum (2026-06) ----
bs = load("biz_status_100").copy()
bs.columns = [c.strip() for c in bs.columns]
bs_dj = bs[bs["시도"] == "대전광역시"].copy()
gu_bs = bs_dj.groupby("시군구")[["당월", "전월", "전년동월"]].sum()
gu_bs["feat_YoY_사업자증감률"] = (gu_bs["당월"] - gu_bs["전년동월"]) / gu_bs["전년동월"] * 100
gu_bs["feat_MoM_사업자증감률"] = (gu_bs["당월"] - gu_bs["전월"]) / gu_bs["전월"] * 100
gu_bs["feat_활성사업자수_2026"] = gu_bs["당월"]
feat = feat.join(gu_bs[["feat_YoY_사업자증감률", "feat_MoM_사업자증감률", "feat_활성사업자수_2026"]])

# ---- FEATURE: business density / industry mix (2026-06 base layer) ----
bl = load("base_layer").copy()
gu_counts = bl["시군구명"].value_counts()
feat["feat_총사업체수"] = gu_counts
# industry diversity (share of top category = concentration risk signal)
mix = bl.groupby(["시군구명", "상권업종대분류명"]).size().unstack(fill_value=0)
mix_share = mix.div(mix.sum(axis=1), axis=0)
feat["feat_음식업비중"] = mix_share["음식"]
feat["feat_소매업비중"] = mix_share["소매"]
feat["feat_최대업종집중도"] = mix_share.max(axis=1)  # HHI-like concentration proxy

# ---- FEATURE: avg survival by business age, city-wide (context, not gu-differentiated) ----
# kept as a note / macro constant, not merged per-gu (no gu breakdown in this file)

feat = feat.round(2)
print(feat.T)

out_path = os.path.join(BASE, "eda", "gu_feature_table.csv")
feat.to_csv(out_path, encoding="utf-8-sig")
print(f"\nSaved -> {out_path}")

# ---- correlation vs target ----
print("\n\n=== correlation with target_생존율 ===")
corr = feat.corr(numeric_only=True)["target_생존율"].sort_values()
print(corr)
