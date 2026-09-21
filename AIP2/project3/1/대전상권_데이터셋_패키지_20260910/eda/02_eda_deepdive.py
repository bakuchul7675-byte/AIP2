# -*- coding: utf-8 -*-
"""EDA step 2: clean & inspect candidate target/feature tables at 구 level."""
import pandas as pd
import os

pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 160)

BASE = r"D:\Desktop\AI Project"
CACHE = os.path.join(BASE, "eda", "cache")

def section(t):
    print("\n" + "=" * 90)
    print(t)
    print("=" * 90)

def load(key):
    return pd.read_pickle(os.path.join(CACHE, f"{key}.pkl"))

DAEJEON_GU = ["동구", "중구", "서구", "유성구", "대덕구"]

# ---------- 1. survival_gu_induty : the likely TARGET table ----------
section("survival_gu_induty -- convert % strings, check ranges")
sv = load("survival_gu_induty").copy()
sv.columns = [c.strip() for c in sv.columns]
sv["생존율_num"] = sv["생존율"].str.rstrip("%").astype(float)
sv["휴폐업율_num"] = sv["휴폐업율"].str.rstrip("%").astype(float)
print(sv[["구", "업종", "총계", "생존율_num", "휴폐업율_num"]].describe(include="all"))
print("\n구별 전체(총계 가중평균) 생존율:")
sv_gu = sv.groupby("구").apply(
    lambda d: pd.Series({
        "총사업체수": d["총계"].sum(),
        "가중생존율": (d["현재_22년9월 기준영업중"].sum() / d["총계"].sum() * 100).round(2),
        "가중폐업율": (d["현재_22년9월 기준 폐업자"].sum() / d["총계"].sum() * 100).round(2),
    })
)
print(sv_gu)

# ---------- 2. biz_status_100 filtered to Daejeon ----------
section("biz_status_100 -- filter 대전광역시, check MoM/YoY change")
bs = load("biz_status_100").copy()
bs.columns = [c.strip() for c in bs.columns]
bs_dj = bs[bs["시도"] == "대전광역시"].copy()
print("대전 rows:", bs_dj.shape)
print("구 리스트:", sorted(bs_dj["시군구"].unique()))
print("업종 개수:", bs_dj["업종"].nunique())
bs_dj["mom_pct"] = ((bs_dj["당월"] - bs_dj["전월"]) / bs_dj["전월"].replace(0, pd.NA) * 100).round(2)
bs_dj["yoy_pct"] = ((bs_dj["당월"] - bs_dj["전년동월"]) / bs_dj["전년동월"].replace(0, pd.NA) * 100).round(2)
print(bs_dj.sort_values("yoy_pct").head(5))
print(bs_dj.sort_values("yoy_pct").tail(5))
gu_level = bs_dj.groupby("시군구")[["당월", "전월", "전년동월"]].sum()
gu_level["yoy_pct"] = ((gu_level["당월"] - gu_level["전년동월"]) / gu_level["전년동월"] * 100).round(2)
print("\n구별 합계 + YoY%:")
print(gu_level)

# ---------- 3. kb_card_sales ----------
section("kb_card_sales -- years covered, missing pattern, melt to long")
kb = load("kb_card_sales").copy()
kb.columns = [c.strip() for c in kb.columns]
print("연도:", sorted(kb["기준년도"].unique()))
print("구:", sorted(kb["구"].unique()))
print("업종 개수:", kb["업종"].nunique())
month_cols = [c for c in kb.columns if "월" in c]
kb_long = kb.melt(id_vars=["기준년도", "구", "업종"], value_vars=month_cols,
                   var_name="월", value_name="매출증감률")
print("결측 비율:", kb_long["매출증감률"].isna().mean().round(3))
print(kb_long.groupby(["기준년도", "구"])["매출증감률"].mean().round(2).unstack())

# ---------- 4. foot_traffic_seogu -- verify ratio vs count ----------
section("foot_traffic_seogu -- does 비율 sum to 100 per group?")
ft = load("foot_traffic_seogu").copy()
check = ft.groupby(["기준년", "기준월", "상권코드"])["비율"].sum()
print(check.describe())
print(check.head(10))
print("\n-> 결론: '비율' 컬럼은 그룹별 합이 ~100이면 성별 구성비(%)이지 유동인구 절대량이 아님")

# ---------- 5. base_layer -- business count per 구/업종 (density feature) ----------
section("base_layer -- 구별 업종대분류별 사업체 수 (density feature candidate)")
bl = load("base_layer").copy()
print("구 리스트:", sorted(bl["시군구명"].unique()))
gu_induty = bl.groupby(["시군구명", "상권업종대분류명"]).size().unstack(fill_value=0)
print(gu_induty)
print("\n구별 총 사업체수:")
print(bl["시군구명"].value_counts())
