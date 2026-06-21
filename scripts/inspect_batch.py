# -*- coding: utf-8 -*-
import pandas as pd

path = "output/batch_markup.xlsx"
xl = pd.ExcelFile(path)
print("Sheets:", xl.sheet_names)
df = pd.read_excel(path, sheet_name="Разметка")
print("Columns:", list(df.columns))
print("Rows:", len(df))
if "description" in df.columns:
    nonempty = df["description"].fillna("").astype(str).str.strip().str.len() > 5
    print("Non-empty description:", int(nonempty.sum()))
mask = df["name"].astype(str).str.contains("Directum", case=False, na=False)
print("Directum rows:", int(mask.sum()))
samples = ["Сервис МЧД.МИГ24", "PlanDesigner", "ZIIoT", "Directum", "1С:Управление", "Optimacros"]
for s in samples:
    m = df["name"].astype(str).str.strip() == s
    if m.any():
        r = df.loc[m].iloc[0]
        d = str(r.get("description", "") or "")
        print(repr(s), "desc_len=", len(d), "Q=", r.get("quadrant_pred"), "B=", r.get("block_pred"))
    else:
        print(repr(s), "NOT FOUND")
