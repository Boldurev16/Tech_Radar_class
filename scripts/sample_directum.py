# -*- coding: utf-8 -*-
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd

df = pd.read_excel(ROOT / "output" / "batch_markup.xlsx", sheet_name="Разметка")
names = """Directum
Сервис МЧД.МИГ24
PlanDesigner
ZIIoT
Optimacros
Postgres Pro
Figma
PROMT Neural Translation Server5
СЭД ТЕЗИС
MineManager
Яндекс.Диск (локальное решение)""".strip().split("\n")

print("name | desc_len | quadrant_pred | block_pred | conf_q/conf_b")
for n in names:
    m = df["name"].astype(str).str.strip() == n.strip()
    if not m.any():
        print(f"{n} | NOT IN FILE")
        continue
    r = df.loc[m].iloc[0]
    dlen = len(str(r.get("description") or ""))
    print(f"{n} | {dlen} | {r['quadrant_pred']} | {r['block_pred']} | {r['quadrant_conf']:.2f}/{r['block_conf']:.2f}")
