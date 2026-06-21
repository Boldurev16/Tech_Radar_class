# -*- coding: utf-8 -*-
"""Re-classify rows in batch_markup.xlsx after description updates."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from classifier import TechRadarClassifier
from evaluate import export_batch_to_excel

INPUT = ROOT / "output" / "batch_markup.xlsx"
DEFAULT_OUTPUT = ROOT / "output" / "batch_markup.xlsx"


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-classify batch markup with updated rules")
    parser.add_argument("--input", default=str(INPUT), help="Input batch markup xlsx")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output batch markup xlsx")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    df_old = pd.read_excel(input_path, sheet_name="Разметка")
    export_df = df_old[["name", "description"]].copy()

    full = pd.read_excel(ROOT / "data" / "source.xlsx", sheet_name="Build your Technology Radar")
    meta = full[["name", "block", "ring"]].drop_duplicates(subset=["name"], keep="first")
    export_df = export_df.merge(meta, on="name", how="left")
    if "quadrant_true" in df_old.columns:
        export_df["quadrant"] = df_old["quadrant_true"]

    clf = TechRadarClassifier(rebuild_prototypes=False)
    print(f"Re-classifying {len(export_df)} rows...")
    export_batch_to_excel(export_df, str(output_path), clf)

    df_new = pd.read_excel(output_path, sheet_name="Разметка")
    changed_q = int((df_new["quadrant_pred"] != df_old["quadrant_pred"]).sum())
    changed_b = int((df_new["block_pred"] != df_old["block_pred"]).sum())
    print(f"Quadrant predictions changed: {changed_q}")
    print(f"Block predictions changed: {changed_b}")
    print(f"Saved: {output_path}")

    samples = ["Directum", "ZIIoT", "Optimacros", "PlanDesigner", "Postgres Pro", "MineManager", "1С:Управление"]
    for s in samples:
        m = df_new["name"].astype(str).str.contains(s, case=False, na=False)
        if m.any():
            r = df_new.loc[m].iloc[0]
            q_conf = pd.to_numeric(r.get("quadrant_confidence"), errors="coerce")
            b_conf = pd.to_numeric(r.get("block_confidence"), errors="coerce")
            print(
                f"  {s}: Q={str(r['quadrant_pred'])[:45]}... "
                f"({q_conf:.2f}) "
                f"B={str(r['block_pred'])[:35]}... "
                f"({b_conf:.2f})"
            )


if __name__ == "__main__":
    main()
