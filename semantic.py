# -*- coding: utf-8 -*-
"""Semantic layer: sentence embeddings and class prototypes."""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from rules import (
    BLOCK_LABELS,
    QUADRANT_LABELS,
    build_weighted_text,
    canonical_block,
    canonical_quadrant,
    is_nn_sputnik_block,
)

DEFAULT_MODEL = "paraphrase-multilingual-mpnet-base-v2"
FALLBACK_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


class SemanticIndex:
    """Embedding prototypes for quadrant and block labels."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        cache_path: str | Path | None = None,
    ) -> None:
        self.model_name = model_name
        self.cache_path = Path(cache_path) if cache_path else None
        self._model: Any = None
        self.quadrant_prototypes: dict[str, np.ndarray] = {}
        self.block_prototypes: dict[str, np.ndarray] = {}
        self.quadrant_labels: list[str] = list(QUADRANT_LABELS)
        self.block_labels: list[str] = list(BLOCK_LABELS)

    @property
    def model(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            try:
                self._model = SentenceTransformer(self.model_name)
            except Exception:
                self._model = SentenceTransformer(FALLBACK_MODEL)
                self.model_name = FALLBACK_MODEL
        return self._model

    def encode(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    def build_from_dataframe(
        self,
        df: pd.DataFrame,
        text_col: str = "text",
        quadrant_col: str = "quadrant",
        block_col: str = "block",
    ) -> None:
        self.quadrant_prototypes = self._build_prototypes(
            df, text_col, quadrant_col, self.quadrant_labels
        )
        self.block_prototypes = self._build_prototypes(
            df, text_col, block_col, self.block_labels
        )

    def _build_prototypes(
        self,
        df: pd.DataFrame,
        text_col: str,
        label_col: str,
        all_labels: list[str],
    ) -> dict[str, np.ndarray]:
        grouped: dict[str, list[str]] = {label: [] for label in all_labels}
        for _, row in df.iterrows():
            text = str(row.get(text_col, "") or "").strip()
            label = str(row.get(label_col, "") or "").strip()
            if not text or not label:
                continue
            if label not in grouped:
                continue
            grouped[label].append(text)

        prototypes: dict[str, np.ndarray] = {}
        for label in all_labels:
            texts = grouped.get(label) or [label]
            embeddings = self.encode(texts)
            prototypes[label] = np.asarray(embeddings.mean(axis=0), dtype=np.float32)
        return prototypes

    def classify(
        self,
        text: str,
        field: str = "quadrant",
        top_k: int = 3,
    ) -> list[tuple[str, float]]:
        prototypes = self.quadrant_prototypes if field == "quadrant" else self.block_prototypes
        if not prototypes:
            return []

        emb = self.encode([text])[0]
        scores = {
            label: float(cosine_similarity([emb], [proto])[0][0])
            for label, proto in prototypes.items()
        }
        ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
        if not ranked:
            return []

        raw = np.array([max(v, 0.0) for _, v in ranked], dtype=float)
        if raw.sum() <= 0:
            probs = np.ones(len(raw)) / len(raw)
        else:
            probs = raw / raw.sum()

        return [(ranked[i][0], round(float(probs[i]), 4)) for i in range(min(top_k, len(ranked)))]

    def save(self, path: str | Path | None = None) -> Path:
        target = Path(path or self.cache_path or "models/prototypes.pkl")
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model_name": self.model_name,
            "quadrant_prototypes": self.quadrant_prototypes,
            "block_prototypes": self.block_prototypes,
        }
        with target.open("wb") as fh:
            pickle.dump(payload, fh)
        return target

    def load(self, path: str | Path | None = None) -> bool:
        target = Path(path or self.cache_path or "models/prototypes.pkl")
        if not target.exists():
            return False
        with target.open("rb") as fh:
            payload = pickle.load(fh)
        self.model_name = payload.get("model_name", self.model_name)
        self.quadrant_prototypes = payload.get("quadrant_prototypes", {})
        self.block_prototypes = payload.get("block_prototypes", {})
        return bool(self.quadrant_prototypes and self.block_prototypes)


def build_training_corpus(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for _, row in df.iterrows():
        name = str(row.get("name", "") or "")
        desc = str(row.get("description", "") or "")
        if is_nn_sputnik_block(row.get("block")):
            continue
        q = canonical_quadrant(row.get("quadrant"))
        b = canonical_block(row.get("block"))
        if not name.strip() or not q or not b:
            continue
        _, _, text = build_weighted_text(name, desc)
        rows.append(
            {
                "name": name,
                "description": desc,
                "text": text,
                "quadrant": q,
                "block": b,
                "ring": str(row.get("ring", "") or ""),
            }
        )
    return pd.DataFrame(rows)


def build_semantic_index(
    class_labels: list[str],
    descriptions_per_class: dict[str, list[str]],
    model_name: str = DEFAULT_MODEL,
) -> dict[str, np.ndarray]:
    index = SemanticIndex(model_name=model_name)
    prototypes: dict[str, np.ndarray] = {}
    for label in class_labels:
        texts = descriptions_per_class.get(label) or [label]
        embeddings = index.encode(texts)
        prototypes[label] = np.asarray(embeddings.mean(axis=0), dtype=np.float32)
    return prototypes


def rebuild_prototypes_cache(path: str | Path | None = None) -> Path:
    from evaluate import load_dataset

    dataset = load_dataset(path)
    index = SemanticIndex(cache_path=Path(__file__).resolve().parent / "models" / "prototypes.pkl")
    index.build_from_dataframe(dataset)
    saved = index.save()
    print(f"[semantic] Rebuilt prototypes on {len(dataset)} rows -> {saved}")
    return saved


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Semantic prototype utilities")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild models/prototypes.pkl")
    parser.add_argument("--data", default=None, help="Path to source.xlsx")
    args = parser.parse_args()
    if args.rebuild:
        rebuild_prototypes_cache(args.data)
    else:
        parser.print_help()
