# -*- coding: utf-8 -*-
"""
EDA step 1: load every 구-level (or 구-relevant) dataset, print shape/columns/
dtypes/missing values, and show a 구 pivot where applicable.
"""
import pandas as pd
import os

pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 160)

BASE = r"D:\Desktop\AI Project"

def section(title):
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def load_csv(path, **kwargs):
    for enc in ["utf-8-sig", "cp949", "utf-8"]:
        try:
            return pd.read_csv(path, encoding=enc, **kwargs)
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"could not decode {path}")


files = {
    "base_layer": "소상공인시장진흥공단_상가(상권)정보_대전_202606.csv",
    "biz_status_100": "국세청_사업자현황_100대 생활업종_20260630.csv",
    "survival_gu_induty": "대전광역시_소상공인 업종별_생존율_폐업율 현황_20220930.csv",
    "survival_period": "대전광역시_소상공인 기간별 생존율_폐업율 현황_20220930.csv",
    "kb_card_sales": "대전광역시_자치구별 신용카드(KB국민카드) 매출액_20200801.csv",
    "ontong_sales_total": "대전광역시_온통대전 월별 매출액_20210930.csv",
    "ontong_sales_induty": "대전광역시_온통대전 월별 업종별 매출액_20210930.csv",
    "foot_traffic_seogu": "대전광역시 서구_상권별 연월별 유동인구 현황_20230510.csv",
}

dfs = {}
for key, fname in files.items():
    path = os.path.join(BASE, fname)
    df = load_csv(path)
    dfs[key] = df
    section(f"{key}  ({fname})")
    print("shape:", df.shape)
    print("columns:", list(df.columns))
    print(df.head(3))
    print("\nmissing values per column:")
    print(df.isna().sum())

# save for reuse by later scripts
os.makedirs(os.path.join(BASE, "eda", "cache"), exist_ok=True)
for key, df in dfs.items():
    df.to_pickle(os.path.join(BASE, "eda", "cache", f"{key}.pkl"))

print("\n\nAll dataframes cached to eda/cache/*.pkl")
