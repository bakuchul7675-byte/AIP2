# -*- coding: utf-8 -*-
"""Merge base_layer (via crosswalk) and biz_status_100 (gu-level broadcast)
into the 구x업종 (n=92) survival target table."""
import pandas as pd
import os

pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 160)

BASE = r"D:\Desktop\AI Project"
CACHE = os.path.join(BASE, "eda", "cache")

def load(key):
    return pd.read_pickle(os.path.join(CACHE, f"{key}.pkl"))

# ---- 1. target table (n=92) ----
sv = load("survival_gu_induty").copy()
sv.columns = [c.strip() for c in sv.columns]
sv["target_생존율"] = sv["생존율"].str.rstrip("%").astype(float)
sv["target_폐업율"] = sv["휴폐업율"].str.rstrip("%").astype(float)
tbl = sv[["구", "업종", "총계", "target_생존율", "target_폐업율"]].copy()
tbl = tbl.rename(columns={"총계": "feat_2022_사업체수"})

# ---- 2. crosswalk: base_layer(10) -> survival(19) ----
CROSSWALK = {
    "음식": "숙박 및 음식점업",
    "숙박": "숙박 및 음식점업",       # 합산 대상 (같은 survival 카테고리로 두 개가 매핑됨)
    "소매": "도매 및 소매업",
    "교육": "교육 서비스업",
    "부동산": "부동산업",
    "예술·스포츠": "예술 스포츠 및 여가관련 서비스업",
    "과학·기술": "전문 과학 및 기술 서비스업",
    "보건의료": "보건업 및 사회복지 서비스업",
    "수리·개인": "협회 및 단체 수리 및 기타 개인 서비스업",
    "시설관리·임대": "사업시설 관리 사업 지원 및 임대 서비스업",
}
bl = load("base_layer").copy()
bl["업종_survival매핑"] = bl["상권업종대분류명"].map(CROSSWALK)
mapped = bl.dropna(subset=["업종_survival매핑"])
gu_induty_2026 = (
    mapped.groupby(["시군구명", "업종_survival매핑"])
    .size()
    .reset_index(name="feat_2026_사업체수")
    .rename(columns={"시군구명": "구", "업종_survival매핑": "업종"})
)
print(f"crosswalk 매핑 성공 row 수: {len(gu_induty_2026)} / target 대상 업종 10종 x 5구 = 50 (나머지 9개 survival 업종은 base_layer에 대응 카테고리 없음)")

tbl = tbl.merge(gu_induty_2026, on=["구", "업종"], how="left")
tbl["feat_2026대비2022_증감률"] = (
    (tbl["feat_2026_사업체수"] - tbl["feat_2022_사업체수"]) / tbl["feat_2022_사업체수"] * 100
).round(2)

# ---- 3. biz_status_100 -> gu-level YoY, broadcast to every 업종 row of that 구 ----
bs = load("biz_status_100").copy()
bs.columns = [c.strip() for c in bs.columns]
bs_dj = bs[bs["시도"] == "대전광역시"]
gu_yoy = bs_dj.groupby("시군구")[["당월", "전월", "전년동월"]].sum()
gu_yoy["feat_구YoY_사업자증감률"] = (
    (gu_yoy["당월"] - gu_yoy["전년동월"]) / gu_yoy["전년동월"] * 100
).round(2)
tbl = tbl.merge(gu_yoy[["feat_구YoY_사업자증감률"]], left_on="구", right_index=True, how="left")

tbl = tbl.round(2)
print("\n최종 병합 테이블 (n=92) 샘플:")
print(tbl.head(15))
print("\nfeat_2026_사업체수 결측 개수 (crosswalk 미매핑 업종):", tbl["feat_2026_사업체수"].isna().sum(), "/", len(tbl))

out = os.path.join(BASE, "eda", "gu_induty_feature_table.csv")
tbl.to_csv(out, index=False, encoding="utf-8-sig")
print(f"\nSaved -> {out}")

print("\n=== correlation with target_생존율 (n=92, listwise-complete rows only) ===")
num = tbl.select_dtypes("number")
print(num.corr()["target_생존율"].sort_values())
print("\n(주의: feat_2026_사업체수 계열은 결측 있는 42개 row 제외하고 계산됨)")
