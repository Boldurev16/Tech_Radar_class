# -*- coding: utf-8 -*-
"""Unit tests for TechRadarClassifier boundary cases."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from classifier import TechRadarClassifier

TEST_CASES = [
    {
        "name": "Агент-переводчик технической документации",
        "description": "Профессиональный ИИ-переводчик, который обучается на документах",
        "expected_quadrant": "Технологии искусственного интеллекта",
        "expected_block": "Блок Аппарата",
    },
    {
        "name": "LLM ЭруДИТ",
        "description": "Сервис умного поиска с использованием больших языковых моделей",
        "expected_quadrant": "Технологии на основе больших языковых моделей",
        "expected_block": "Блок СВП - Производственный директор",
    },
    {
        "name": "Смарт-контракты для автоматизации закупок МТР",
        "description": "Цифровые программируемые договоры для закупок материально-технических ресурсов",
        "expected_quadrant": "Технологии блокчейн",
        "expected_block": "Блок внутреннего контроля и риск-менеджмента",
    },
    {
        "name": "Беспроводной мониторинг состояния футеровки печей",
        "description": "Система контроля огнеупорной футеровки на основе беспроводных датчиков температуры",
        "expected_quadrant": "Технологии IoT и интернет вещей",
        "expected_block": "Блок СВП - Производственный директор",
    },
]


@pytest.fixture(scope="module")
def classifier() -> TechRadarClassifier:
    return TechRadarClassifier(rebuild_prototypes=False)


@pytest.mark.parametrize("case", TEST_CASES, ids=[c["name"] for c in TEST_CASES])
def test_boundary_cases(classifier: TechRadarClassifier, case: dict) -> None:
    result = classifier.classify(case["name"], case["description"])
    assert result.quadrant == case["expected_quadrant"], (
        f"quadrant: expected {case['expected_quadrant']}, got {result.quadrant}; "
        f"top3={result.quadrant_top3}; method={result.classification_method}"
    )
    assert result.block == case["expected_block"], (
        f"block: expected {case['expected_block']}, got {result.block}; "
        f"top3={result.block_top3}; warnings={result.warnings}"
    )


def test_result_fields(classifier: TechRadarClassifier) -> None:
    result = classifier.classify("LLM ЭруДИТ", "Сервис умного поиска")
    assert 0.0 <= result.quadrant_confidence <= 1.0
    assert 0.0 <= result.block_confidence <= 1.0
    assert len(result.quadrant_top3) <= 3
    assert len(result.block_top3) <= 3
    assert result.classification_method in {
        "rule_based", "semantic", "ensemble", "default", "semantic_inferred"
    }


def test_batch_mode(classifier: TechRadarClassifier) -> None:
    import pandas as pd

    df = pd.DataFrame(
        [
            {"name": c["name"], "description": c["description"]}
            for c in TEST_CASES[:2]
        ]
    )
    out = classifier.classify_batch(df)
    assert len(out) == 2
    assert "quadrant" in out.columns
    assert "block" in out.columns
