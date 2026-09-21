# -*- coding: utf-8 -*-
"""Pull all Daejeon (areaCode=3) TourAPI listings for the content types we
care about, paginate fully, and save one consolidated CSV."""
import requests
import pandas as pd
import time

SERVICE_KEY = "b795a2ed228fe0d15b8c43be463a571b288579ae9c864690ee1a7817d237492e"
ENDPOINT = "https://apis.data.go.kr/B551011/KorService2/areaBasedList2"

CONTENT_TYPES = {
    "12": "관광지",
    "14": "문화시설",
    "15": "축제행사",
    "28": "레포츠",
    "39": "음식점",
}

rows = []
for ctype, label in CONTENT_TYPES.items():
    page = 1
    while True:
        params = {
            "serviceKey": SERVICE_KEY,
            "numOfRows": 100,
            "pageNo": page,
            "MobileOS": "ETC",
            "MobileApp": "DaejeonAI",
            "_type": "json",
            "areaCode": 3,
            "contentTypeId": ctype,
        }
        r = requests.get(ENDPOINT, params=params, timeout=20)
        data = r.json()
        header = data.get("response", {}).get("header", {})
        if header.get("resultCode") != "0000":
            print(f"[{label}] page {page} error: {header}")
            break
        body = data["response"]["body"]
        total = body.get("totalCount", 0)
        items = body.get("items", {})
        item_list = items.get("item", []) if items else []
        if isinstance(item_list, dict):
            item_list = [item_list]
        for it in item_list:
            it["contenttype_label"] = label
        rows.extend(item_list)
        print(f"[{label}] page {page}: got {len(item_list)} (total={total})")
        if page * 100 >= total or not item_list:
            break
        page += 1
        time.sleep(0.2)

df = pd.DataFrame(rows)
print("\n총 수집 row 수:", len(df))
print(df["contenttype_label"].value_counts())

out = r"D:\Desktop\AI Project\한국관광공사_TourAPI_대전_관광지음식점_20260910.csv"
df.to_csv(out, index=False, encoding="utf-8-sig")
print(f"\nSaved -> {out}")
