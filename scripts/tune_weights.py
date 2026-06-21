# -*- coding: utf-8 -*-
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from classifier import TechRadarClassifier
from evaluate import evaluate, load_dataset, train_test_split_df

dataset = load_dataset()
train_df, test_df = train_test_split_df(dataset, test_ratio=0.2, seed=42)
train_inner, _ = train_test_split_df(train_df, test_ratio=0.2, seed=43)
clf = TechRadarClassifier(rebuild_prototypes=False)
clf.fit_prototypes(train_inner)

for q, b in [(0.4, 0.6), (0.2, 0.8), (0.1, 0.9), (0.6, 0.7), (0.5, 0.8)]:
    clf.set_ensemble_weights(quadrant=q, block=b)
    m = evaluate(test_df, clf)
    print(
        f"q={q} b={b} -> qF1={m['quadrant_macro_f1']:.3f} "
        f"bF1={m['block_macro_f1']:.3f} joint={m['joint_accuracy']:.3f}"
    )
