# -*- coding: utf-8 -*-
"""Tech Radar scenario classifier."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from evaluate import (
    DATA_PATH,
    ENSEMBLE_WEIGHTS_PATH,
    ITERATION3_METRICS_PATH,
    block_quadrant_matrix,
    class_distribution,
    compatibility_matrix,
    evaluate,
    export_batch_to_excel,
    load_dataset,
    load_full_export_dataset,
    save_metrics_json,
    train_test_split_df,
)
from rules import (
    BLOCK_KEYWORDS,
    BLOCK_LABELS,
    BLOCK_PRIORITY_RULES,
    DEFAULT_BLOCK,
    DEFAULT_QUADRANT,
    LOW_CONFIDENCE_THRESHOLD,
    PRODUCTION_BLOCK_FALLBACK,
    QUADRANT_KEYWORDS,
    QUADRANT_LABELS,
    QUADRANT_PRIORITY_RULES,
    apply_process_code_boost,
    apply_quadrant_disambiguation,
    build_weighted_text,
    disambiguate_blocks,
    is_nn_sputnik_block,
    normalize_ring,
    score_labels,
    scores_to_ranking,
)
from evaluate import load_block_process_codes
from semantic import SemanticIndex

Mode = Literal["inference", "batch", "evaluate"]

RING_QUADRANT_PRIOR: dict[str, dict[str, float | bool]] = {
    "Перспективные Российские технологии": {
        "Технологии импортозамещения и реновация": 0.6,
        "_apply_only_if_conf_below": 0.70,
    },
    "Перспективные Мировые технологии": {
        "Технологии импортозамещения и реновация": -0.3,
        "_apply_always": True,
    },
    "Внедряется": {"_conf_boost": 0.05},
    "Прототипируется": {"_conf_boost": 0.03},
}


@dataclass
class ClassificationResult:
    name: str
    quadrant: str
    block: str
    quadrant_confidence: float
    block_confidence: float
    quadrant_top3: list[tuple[str, float]]
    block_top3: list[tuple[str, float]]
    classification_method: str
    warnings: list[str] = field(default_factory=list)


class TechRadarClassifier:
    """Two-level classifier: rule-based layer + semantic prototypes."""

    def __init__(
        self,
        data_path: str | Path | None = None,
        model_name: str = "paraphrase-multilingual-mpnet-base-v2",
        prototypes_path: str | Path | None = None,
        rebuild_prototypes: bool = False,
        random_seed: int = 42,
    ) -> None:
        self.data_path = Path(data_path or DATA_PATH)
        self.prototypes_path = Path(
            prototypes_path or Path(__file__).resolve().parent / "models" / "prototypes.pkl"
        )
        self.random_seed = random_seed
        self.optimized_weight_rule = 0.4
        self.optimized_weight_rule_quadrant = 0.4
        self.optimized_weight_rule_block = 0.6
        self.semantic = SemanticIndex(model_name=model_name, cache_path=self.prototypes_path)
        self.process_codes = load_block_process_codes(self.data_path)
        self._load_ensemble_weights()

        self._dataset = load_dataset(self.data_path)
        self.quadrant_priors = self._compute_priors(self._dataset, "quadrant", QUADRANT_LABELS)
        self.block_priors = self._compute_priors(self._dataset, "block", BLOCK_LABELS)
        self.compat_q_b = compatibility_matrix(self._dataset)
        self.compat_b_q = block_quadrant_matrix(self._dataset)

        if rebuild_prototypes or not self.semantic.load(self.prototypes_path):
            self.fit_prototypes(self._dataset)
        else:
            self.semantic.model  # warm up model

    def _load_ensemble_weights(self) -> None:
        if ENSEMBLE_WEIGHTS_PATH.exists():
            with ENSEMBLE_WEIGHTS_PATH.open(encoding="utf-8") as fh:
                payload = json.load(fh)
            self.optimized_weight_rule = float(payload.get("optimized_weight_rule", 0.4))
            self.optimized_weight_rule_quadrant = float(
                payload.get("optimized_weight_rule_quadrant", self.optimized_weight_rule)
            )
            self.optimized_weight_rule_block = float(
                payload.get("optimized_weight_rule_block", 0.6)
            )

    def set_ensemble_weights(
        self,
        weight_rule: float | None = None,
        *,
        quadrant: float | None = None,
        block: float | None = None,
    ) -> None:
        if weight_rule is not None:
            self.optimized_weight_rule = max(0.0, min(1.0, float(weight_rule)))
            self.optimized_weight_rule_quadrant = self.optimized_weight_rule
            self.optimized_weight_rule_block = self.optimized_weight_rule
        if quadrant is not None:
            self.optimized_weight_rule_quadrant = max(0.0, min(1.0, float(quadrant)))
        if block is not None:
            self.optimized_weight_rule_block = max(0.0, min(1.0, float(block)))

    def _resolve_ensemble_weights(
        self,
        rule_conf: float,
        field: str = "quadrant",
    ) -> tuple[float, float]:
        if rule_conf >= 0.8:
            return 0.9, 0.1
        if rule_conf < 0.5:
            return 0.1, 0.9
        base = (
            self.optimized_weight_rule_quadrant
            if field == "quadrant"
            else self.optimized_weight_rule_block
        )
        return base, 1.0 - base

    def fit_prototypes(self, df: pd.DataFrame | None = None) -> None:
        corpus = df if df is not None else self._dataset
        self.semantic.build_from_dataframe(corpus)
        self.semantic.save(self.prototypes_path)

    @staticmethod
    def _compute_priors(df: pd.DataFrame, column: str, labels: list[str]) -> dict[str, float]:
        counts = df[column].value_counts() if not df.empty else pd.Series(dtype=int)
        total = max(int(counts.sum()), 1)
        priors = {label: float(counts.get(label, 0)) / total for label in labels}
        smooth = 1e-3
        denom = sum(priors.values()) + smooth * len(labels)
        return {label: (priors[label] + smooth) / denom for label in labels}

    def _merge_scores(
        self,
        rule_scores: dict[str, float],
        semantic_ranking: list[tuple[str, float]],
        labels: list[str],
        priors: dict[str, float],
        compat_row: pd.Series | None,
        field: str = "quadrant",
    ) -> tuple[dict[str, float], str]:
        semantic_scores = {label: 0.0 for label in labels}
        for label, prob in semantic_ranking:
            semantic_scores[label] = prob

        rule_top = max(rule_scores, key=lambda k: rule_scores[k]) if rule_scores else labels[0]
        rule_conf = rule_scores.get(rule_top, 0.0)
        semantic_top = semantic_ranking[0][0] if semantic_ranking else rule_top
        semantic_conf = semantic_ranking[0][1] if semantic_ranking else 0.0

        conflict = (
            rule_conf >= 0.45
            and semantic_conf >= 0.18
            and rule_top != semantic_top
        )
        weight_rule, weight_semantic = self._resolve_ensemble_weights(rule_conf, field=field)

        if rule_conf >= 0.75 and not conflict:
            method = "rule_based"
            merged = {label: rule_scores.get(label, 0.0) for label in labels}
            prior_weight = 0.0
            compat_weight = 0.0
        elif rule_conf < 0.35 and semantic_ranking:
            method = "semantic"
            merged = semantic_scores.copy()
            prior_weight = 0.35
            compat_weight = 0.35
        elif conflict:
            method = "ensemble"
            merged = {
                label: weight_rule * rule_scores.get(label, 0.0)
                + weight_semantic * semantic_scores.get(label, 0.0)
                for label in labels
            }
            prior_weight = 0.35
            compat_weight = 0.35
        elif semantic_ranking and semantic_conf > rule_conf:
            method = "semantic"
            merged = {
                label: (1 - weight_semantic) * rule_scores.get(label, 0.0)
                + weight_semantic * semantic_scores.get(label, 0.0)
                for label in labels
            }
            prior_weight = 0.35
            compat_weight = 0.25
        else:
            method = "rule_based"
            merged = {
                label: weight_rule * rule_scores.get(label, 0.0)
                + weight_semantic * semantic_scores.get(label, 0.0)
                for label in labels
            }
            prior_weight = 0.35
            compat_weight = 0.25

        for label in labels:
            if prior_weight > 0:
                merged[label] *= priors.get(label, 1e-6) ** prior_weight
            if compat_row is not None and label in compat_row.index and compat_weight > 0:
                merged[label] *= float(compat_row.get(label, 1e-6)) ** compat_weight

        total = sum(merged.values()) or 1.0
        merged = {label: value / total for label, value in merged.items()}
        return merged, method

    def _apply_ring_prior(self, ring: str | None, quadrant_scores: dict[str, float]) -> dict[str, float]:
        norm_ring = normalize_ring(ring)
        prior = RING_QUADRANT_PRIOR.get(norm_ring, {})
        if not prior:
            return quadrant_scores

        adjusted = quadrant_scores.copy()
        threshold = float(prior.get("_apply_only_if_conf_below", 1.0))
        max_conf = max(quadrant_scores.values()) if quadrant_scores else 0.0

        for quadrant, delta in prior.items():
            if str(quadrant).startswith("_"):
                continue
            if max_conf < threshold or prior.get("_apply_always"):
                adjusted[quadrant] = adjusted.get(quadrant, 0.0) + float(delta)

        total = sum(adjusted.values()) or 1.0
        return {label: value / total for label, value in adjusted.items()}

    def _ring_conf_boost(self, ring: str | None) -> float:
        norm_ring = normalize_ring(ring)
        prior = RING_QUADRANT_PRIOR.get(norm_ring, {})
        return float(prior.get("_conf_boost", 0.0))

    def _classify_quadrant(
        self,
        name: str,
        description: str,
        block_hint: str | None = None,
        ring: str | None = None,
    ) -> tuple[str, float, list[tuple[str, float]], str]:
        _, _, full = build_weighted_text(name, description)
        rule_scores = score_labels(
            name,
            description,
            QUADRANT_KEYWORDS,
            QUADRANT_LABELS,
            QUADRANT_PRIORITY_RULES,
        )
        semantic_ranking = self.semantic.classify(full, field="quadrant", top_k=3)
        compat_row = None
        if block_hint and block_hint in self.compat_b_q.index:
            compat_row = self.compat_b_q.loc[block_hint]

        merged, method = self._merge_scores(
            rule_scores,
            semantic_ranking,
            QUADRANT_LABELS,
            self.quadrant_priors,
            compat_row,
            field="quadrant",
        )
        merged = apply_quadrant_disambiguation(full, ring, merged)
        merged = self._apply_ring_prior(ring, merged)
        ranking = scores_to_ranking(merged, top_k=3)
        if not ranking:
            return DEFAULT_QUADRANT, 0.0, [], "default"
        top_label, _ = ranking[0]
        top_conf = min(
            1.0,
            max(
                rule_scores.get(top_label, 0.0),
                next((prob for label, prob in semantic_ranking if label == top_label), 0.0),
                merged.get(top_label, 0.0),
            ) + self._ring_conf_boost(ring),
        )
        return top_label, round(top_conf, 4), ranking, method

    def _classify_block(
        self,
        name: str,
        description: str,
        quadrant_hint: str | None = None,
    ) -> tuple[str, float, list[tuple[str, float]], str]:
        _, _, full = build_weighted_text(name, description)
        rule_scores = score_labels(
            name,
            description,
            BLOCK_KEYWORDS,
            BLOCK_LABELS,
            BLOCK_PRIORITY_RULES,
        )
        apply_process_code_boost(full, rule_scores, self.process_codes)
        rule_scores = disambiguate_blocks(name, description, rule_scores)

        semantic_ranking = self.semantic.classify(full, field="block", top_k=3)
        compat_row = None
        if quadrant_hint and quadrant_hint in self.compat_q_b.index:
            compat_row = self.compat_q_b.loc[quadrant_hint]

        merged, method = self._merge_scores(
            rule_scores,
            semantic_ranking,
            BLOCK_LABELS,
            self.block_priors,
            compat_row,
            field="block",
        )
        ranking = scores_to_ranking(merged, top_k=3)
        if not ranking:
            return DEFAULT_BLOCK, 0.0, [], "default"
        top_label, _ = ranking[0]
        top_conf = min(
            1.0,
            max(
                rule_scores.get(top_label, 0.0),
                next((prob for label, prob in semantic_ranking if label == top_label), 0.0),
                merged.get(top_label, 0.0),
            ),
        )
        return top_label, round(top_conf, 4), ranking, method

    def classify(
        self,
        name: str,
        description: str = "",
        raw_block: str | None = None,
        ring: str | None = None,
    ) -> ClassificationResult:
        sputnik_input = bool(raw_block and is_nn_sputnik_block(raw_block))
        quadrant, q_conf, q_top3, q_method = self._classify_quadrant(
            name, description, ring=ring
        )
        block, block_conf, block_top3, block_method = self._classify_block(
            name, description, quadrant_hint=quadrant
        )

        if q_conf < 0.55:
            quadrant2, q_conf2, q_top3_2, q_method2 = self._classify_quadrant(
                name, description, block_hint=block, ring=ring
            )
            if quadrant2 == quadrant and q_conf2 > q_conf:
                quadrant, q_conf, q_top3, q_method = quadrant2, q_conf2, q_top3_2, q_method2
                block, block_conf, block_top3, block_method = self._classify_block(
                    name, description, quadrant_hint=quadrant
                )

        method = q_method if q_method == block_method else "ensemble"
        if sputnik_input:
            method = "semantic_inferred" if block_method == "semantic" else method
        warnings: list[str] = []
        if sputnik_input:
            warnings.append("block inferred (source: НН-Спутник)")
            warnings.append("raw_block=НН-Спутник excluded: block predicted from content")
        if q_conf < LOW_CONFIDENCE_THRESHOLD:
            warnings.append(f"low_quadrant_confidence:{q_conf:.2f}")
        if block_conf < LOW_CONFIDENCE_THRESHOLD:
            warnings.append(f"low_block_confidence:{block_conf:.2f}")
        if q_method != block_method:
            warnings.append(f"layer_conflict:quadrant={q_method},block={block_method}")
        if block == PRODUCTION_BLOCK_FALLBACK and block_conf < 0.55:
            warnings.append("production_block_fallback")

        return ClassificationResult(
            name=name,
            quadrant=quadrant,
            block=block,
            quadrant_confidence=round(q_conf, 4),
            block_confidence=round(block_conf, 4),
            quadrant_top3=q_top3,
            block_top3=block_top3,
            classification_method=method,
            warnings=warnings,
        )

    def classify_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for _, row in df.iterrows():
            result = self.classify(
                str(row.get("name", "") or ""),
                str(row.get("description", "") or ""),
                raw_block=row.get("block") if "block" in df.columns else None,
                ring=row.get("ring") if "ring" in df.columns else None,
            )
            rows.append(
                {
                    "name": result.name,
                    "quadrant": result.quadrant,
                    "block": result.block,
                    "quadrant_confidence": result.quadrant_confidence,
                    "block_confidence": result.block_confidence,
                    "quadrant_top3": result.quadrant_top3,
                    "block_top3": result.block_top3,
                    "classification_method": result.classification_method,
                    "warnings": result.warnings,
                }
            )
        return pd.DataFrame(rows)

    def run_evaluate(
        self,
        holdout_ratio: float = 0.2,
        stratify: str = "quadrant",
        rebuild_prototypes: bool = True,
    ) -> dict:
        stratify_col = "multi" if stratify == "multi" else "quadrant"
        train_df, test_df = train_test_split_df(
            self._dataset,
            test_ratio=holdout_ratio,
            seed=self.random_seed,
            stratify_col=stratify_col,
        )
        if rebuild_prototypes:
            self.fit_prototypes(train_df)
        metrics = evaluate(test_df, self)
        metrics["class_distribution"] = class_distribution(self._dataset)
        metrics["train_size"] = len(train_df)
        metrics["test_size"] = len(test_df)
        metrics["dataset_size"] = len(self._dataset)
        metrics["stratify"] = stratify_col
        metrics["nn_sputnik_excluded"] = True
        return metrics


def run_iteration3_eval(stratify: str = "multi", export: bool = True) -> dict:
    clf = TechRadarClassifier(rebuild_prototypes=True)
    metrics = clf.run_evaluate(stratify=stratify, rebuild_prototypes=True)
    metrics["baseline_iteration2"] = {
        "block_macro_f1": 0.238,
        "quadrant_macro_f1": 0.401,
        "joint_accuracy": 0.447,
    }
    save_metrics_json(metrics, ITERATION3_METRICS_PATH)
    if export:
        export_path = Path(__file__).resolve().parent / "output" / "batch_markup.xlsx"
        export_batch_to_excel(load_full_export_dataset(), str(export_path), clf)
        metrics["export_path"] = str(export_path)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Tech Radar classifier")
    parser.add_argument("--evaluate", action="store_true", help="Run hold-out evaluation")
    parser.add_argument(
        "--stratify",
        default="multi",
        choices=["quadrant", "multi"],
        help="Stratification strategy for hold-out split",
    )
    parser.add_argument("--rebuild-prototypes", action="store_true", help="Rebuild prototypes only")
    args = parser.parse_args()

    if args.rebuild_prototypes:
        from semantic import rebuild_prototypes_cache

        rebuild_prototypes_cache()
        return

    if args.evaluate:
        metrics = run_iteration3_eval(stratify=args.stratify, export=True)
        print("Iteration 3 evaluation (NN-Sputnik excluded)")
        print(f"  dataset size: {metrics['dataset_size']} (train={metrics['train_size']}, test={metrics['test_size']})")
        print(f"  stratify: {metrics['stratify']}")
        print(f"  quadrant macro F1: {metrics['quadrant_macro_f1']:.3f}")
        print(f"  block macro F1:    {metrics['block_macro_f1']:.3f}")
        print(f"  joint accuracy:    {metrics['joint_accuracy']:.3f}")
        print(f"  metrics saved: {ITERATION3_METRICS_PATH}")
        if "export_path" in metrics:
            print(f"  export: {metrics['export_path']}")
        return

    metrics = run_iteration3_eval(stratify="multi", export=False)
    print("Default run: iteration 3 metrics")
    print(f"  block macro F1: {metrics['block_macro_f1']:.3f}")


if __name__ == "__main__":
    main()
