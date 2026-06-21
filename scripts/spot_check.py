# -*- coding: utf-8 -*-
"""
Быстрая проверка конкретных записей из датасета по имени продукта/сценария.
Выводит: quadrant_pred, block_pred, conf, top3, method, warnings.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from classifier import TechRadarClassifier
from evaluate import DATA_PATH
from rules import canonical_block, canonical_quadrant


def load_spot_check_dataset() -> pd.DataFrame:
    raw = pd.read_excel(DATA_PATH, sheet_name="Build your Technology Radar")
    raw = raw.rename(columns={"block": "block_raw"})
    raw["quadrant_true"] = raw["quadrant"].map(canonical_quadrant)
    raw["block_true"] = raw["block_raw"].map(canonical_block)

    batch_path = ROOT / "output" / "batch_markup.xlsx"
    if batch_path.exists():
        batch = pd.read_excel(batch_path, sheet_name="Разметка")
        desc = batch[["name", "description"]].drop_duplicates(subset=["name"], keep="first")
        raw = raw.drop(columns=["description"], errors="ignore").merge(desc, on="name", how="left")

    return raw


def spot_check(names: list[str]) -> None:
    df = load_spot_check_dataset()
    clf = TechRadarClassifier(rebuild_prototypes=False)

    for name in names:
        needle = name.strip()
        if not needle:
            continue
        rows = df[df["name"].astype(str).str.contains(needle, case=False, na=False)]
        if rows.empty:
            print(f"[NOT FOUND] {name}")
            continue
        for _, row in rows.iterrows():
            result = clf.classify(
                str(row["name"]),
                str(row.get("description", "") or ""),
                ring=row.get("ring", ""),
                raw_block=row.get("block_raw", ""),
            )
            print(f"\n{'=' * 60}")
            print(f"Name:     {row['name']}")
            print(f"Ring:     {row.get('ring', 'N/A')}")
            print(f"Q_pred:   {result.quadrant} ({result.quadrant_confidence:.2f})")
            print(f"Q_true:   {row.get('quadrant_true', 'N/A')}")
            print(f"B_pred:   {result.block} ({result.block_confidence:.2f})")
            print(f"B_true:   {row.get('block_true', 'N/A')}")
            print(f"Method:   {result.classification_method}")
            if result.quadrant_top3:
                print(f"Q_top3:   {result.quadrant_top3}")
            if result.block_top3:
                print(f"B_top3:   {result.block_top3}")
            if result.warnings:
                print(f"Warnings: {result.warnings}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Spot-check classifier on named records")
    parser.add_argument(
        "--records",
        default="",
        help='Comma-separated product names, e.g. "Directum,PlanDesigner"',
    )
    args = parser.parse_args()
    names = [part.strip() for part in args.records.split(",") if part.strip()]
    if not names:
        print('Usage: python scripts/spot_check.py --records "Directum,PlanDesigner"')
        sys.exit(1)
    spot_check(names)


if __name__ == "__main__":
    main()
