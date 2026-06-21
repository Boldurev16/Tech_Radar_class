# -*- coding: utf-8 -*-
"""Retune ensemble weights and rebuild prototypes from manual markup."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from classifier import TechRadarClassifier
from evaluate import (
    ENSEMBLE_WEIGHTS_PATH,
    RESULTS_DIR,
    evaluate,
    load_dataset,
    optimize_ensemble_weights,
    train_test_split_df,
)
from evaluate import block_quadrant_matrix, compatibility_matrix
from rules import BLOCK_LABELS, QUADRANT_LABELS

MANUAL_PATH = ROOT / "data" / "source_16.06.xlsx"
METRICS_PATH = RESULTS_DIR / "retune_manual_metrics.json"


def refresh_classifier_stats(clf: TechRadarClassifier, df) -> None:
    clf._dataset = df.reset_index(drop=True)
    clf.quadrant_priors = clf._compute_priors(clf._dataset, "quadrant", QUADRANT_LABELS)
    clf.block_priors = clf._compute_priors(clf._dataset, "block", BLOCK_LABELS)
    clf.compat_q_b = compatibility_matrix(clf._dataset)
    clf.compat_b_q = block_quadrant_matrix(clf._dataset)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    dataset = load_dataset(MANUAL_PATH)
    train_df, test_df = train_test_split_df(
        dataset, test_ratio=0.2, seed=42, stratify_col="multi"
    )
    train_inner, val_df = train_test_split_df(
        train_df, test_ratio=0.2, seed=43, stratify_col="multi"
    )

    print(f"[data] manual corpus: {len(dataset)} rows (train={len(train_df)}, test={len(test_df)})")
    print(f"[data] validation split: {len(val_df)} rows")

    clf = TechRadarClassifier(data_path=MANUAL_PATH, rebuild_prototypes=False)
    refresh_classifier_stats(clf, train_df)

    baseline = evaluate(test_df, clf)
    print(
        "[baseline] current weights + old prototypes on manual test: "
        f"qF1={baseline['quadrant_macro_f1']:.3f} "
        f"bF1={baseline['block_macro_f1']:.3f} "
        f"joint={baseline['joint_accuracy']:.3f}"
    )

    print("[prototypes] rebuilding on train split...")
    clf.fit_prototypes(train_df)
    refresh_classifier_stats(clf, train_df)

    after_proto = evaluate(test_df, clf)
    print(
        "[prototypes] after rebuild on manual train: "
        f"qF1={after_proto['quadrant_macro_f1']:.3f} "
        f"bF1={after_proto['block_macro_f1']:.3f} "
        f"joint={after_proto['joint_accuracy']:.3f}"
    )

    print("[weights] grid search on validation split...")
    payload = optimize_ensemble_weights(clf, val_df, output_path=ENSEMBLE_WEIGHTS_PATH)
    payload["source"] = str(MANUAL_PATH)
    payload["train_size"] = len(train_inner)
    payload["val_size"] = len(val_df)
    payload["test_size"] = len(test_df)
    payload["dataset_size"] = len(dataset)
    payload["baseline_test"] = {
        "quadrant_macro_f1": round(baseline["quadrant_macro_f1"], 4),
        "block_macro_f1": round(baseline["block_macro_f1"], 4),
        "joint_accuracy": round(baseline["joint_accuracy"], 4),
    }
    payload["after_prototypes_test"] = {
        "quadrant_macro_f1": round(after_proto["quadrant_macro_f1"], 4),
        "block_macro_f1": round(after_proto["block_macro_f1"], 4),
        "joint_accuracy": round(after_proto["joint_accuracy"], 4),
    }

    final_test = evaluate(test_df, clf)
    payload["final_test"] = {
        "quadrant_macro_f1": round(final_test["quadrant_macro_f1"], 4),
        "block_macro_f1": round(final_test["block_macro_f1"], 4),
        "joint_accuracy": round(final_test["joint_accuracy"], 4),
        "quadrant_accuracy": round(final_test["quadrant_accuracy"], 4),
        "block_accuracy": round(final_test["block_accuracy"], 4),
    }
    payload["notes"] = (
        "Retuned on source_16.06.xlsx manual markup; "
        "prototypes rebuilt on train split; weights optimized on inner val split"
    )

    with ENSEMBLE_WEIGHTS_PATH.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    with METRICS_PATH.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("RETUNE COMPLETE")
    print("=" * 60)
    print(f"  quadrant weight (rule): {payload['optimized_weight_rule_quadrant']}")
    print(f"  block weight (rule):    {payload['optimized_weight_rule_block']}")
    print(f"  val qF1: {payload['optimized_quadrant_macro_f1']:.3f}  "
          f"val bF1: {payload['optimized_block_macro_f1']:.3f}")
    print(
        f"  test qF1: {payload['final_test']['quadrant_macro_f1']:.3f}  "
        f"test bF1: {payload['final_test']['block_macro_f1']:.3f}  "
        f"joint: {payload['final_test']['joint_accuracy']:.3f}"
    )
    print(f"  weights: {ENSEMBLE_WEIGHTS_PATH}")
    print(f"  metrics: {METRICS_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
