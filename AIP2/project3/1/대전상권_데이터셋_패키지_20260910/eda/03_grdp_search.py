# -*- coding: utf-8 -*-
"""Find which pages of the GRDP PDF contain Daejeon-gu level tables."""
import pdfplumber
import re

PATH = r"D:\Desktop\AI Project\대전광역시_자치구 단위 지역내총생산_20191231.pdf"
GU = ["동구", "중구", "서구", "유성구", "대덕구"]

with pdfplumber.open(PATH) as pdf:
    print("total pages:", len(pdf.pages))
    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        hits = sum(1 for g in GU if g in text)
        if hits >= 3:  # page mentions at least 3 of the 5 districts -> likely a gu-comparison table
            print(f"--- page {i+1} (gu mentions={hits}) ---")
            print(text[:600])
            print("...")
