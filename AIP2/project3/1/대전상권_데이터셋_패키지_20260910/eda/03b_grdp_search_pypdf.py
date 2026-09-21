# -*- coding: utf-8 -*-
"""Faster GRDP page search using pypdf instead of pdfplumber."""
import pypdf

PATH = r"D:\Desktop\AI Project\대전광역시_자치구 단위 지역내총생산_20191231.pdf"
GU = ["동구", "중구", "서구", "유성구", "대덕구"]

reader = pypdf.PdfReader(PATH)
print("total pages:", len(reader.pages))
for i, page in enumerate(reader.pages):
    try:
        text = page.extract_text() or ""
    except Exception as e:
        print(f"page {i+1}: extract error {e}")
        continue
    hits = sum(1 for g in GU if g in text)
    if hits >= 3:
        print(f"--- page {i+1} (gu mentions={hits}) ---")
        print(text[:500])
        print("...")
