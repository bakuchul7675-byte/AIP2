# -*- coding: utf-8 -*-
"""Add GRDP (2019, extracted from the PDF table on page 19) to the 5-gu table."""
import pandas as pd

GRDP = {
    "동구":  {"grdp_2019_십억원": 3686, "grdp_증감률": 5.2, "grdp_비중": 8.6},
    "중구":  {"grdp_2019_십억원": 5086, "grdp_증감률": 3.7, "grdp_비중": 11.8},
    "서구":  {"grdp_2019_십억원": 12715, "grdp_증감률": 5.6, "grdp_비중": 29.5},
    "유성구": {"grdp_2019_십억원": 14020, "grdp_증감률": 3.3, "grdp_비중": 32.5},
    "대덕구": {"grdp_2019_십억원": 7585, "grdp_증감률": 4.2, "grdp_비중": 17.6},
}
grdp_df = pd.DataFrame(GRDP).T
grdp_df.index.name = "구"

feat = pd.read_csv(r"D:\Desktop\AI Project\eda\gu_feature_table.csv", index_col="구", encoding="utf-8-sig")
feat = feat.join(grdp_df)
feat.to_csv(r"D:\Desktop\AI Project\eda\gu_feature_table.csv", encoding="utf-8-sig")
print(feat.T)
print("\n=== correlation with target_생존율 (n=5, 참고용) ===")
print(feat.corr(numeric_only=True)["target_생존율"].sort_values())
