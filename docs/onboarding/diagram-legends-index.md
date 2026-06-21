# Diagram Legends Index

Единый справочник обозначений для Mermaid-диаграмм в `docs/`.

> 💬 **RU:** Читайте перед остальными диаграммами. Термины здесь same as in code (`rules.py`, `classifier.py`). При добавлении новой диаграммы — не вводите новые обозначения без записи сюда.

---

## Abbreviations

| Term | Russian explanation |
|------|---------------------|
| **Quadrant** | Технологическое направление radar (24 класса) |
| **Block** | Блок бизнес-процессов / org owner (16 классов) |
| **Ring** | Кольцо TRL зрелости («Внедряется», «Перспективные Российские…») |
| **NN-Sputnik** | Метатег «НН-Спутник. Вне КПМ» — исключён из обучения |
| **Rule layer** | Детерминированные keywords/regex в `rules.py` |
| **Semantic layer** | Embeddings + prototypes в `semantic.py` |
| **Ensemble** | Слияние rule + semantic в `_merge_scores` |
| **Proto** | Центроид embedding класса в `prototypes.pkl` |
| **Compat matrix** | Co-occurrence block↔quadrant из training data |
| **Prior** | Частота класса в training corpus |
| **SoT** | Source of truth — Excel file |
| **HF** | HuggingFace Hub (загрузка модели) |

> 💬 **RU:** Аббревиатуры используются во всех docs на английском; русская колонка — для onboarding. NN-Sputnik и Ring — domain-specific; новички часто путают ring (TRL) с quadrant.

---

## Node Shapes (flowchart)

| Shape | Meaning | Example |
|-------|---------|---------|
| `["..."]` | Process / component | `Clf["TechRadarClassifier"]` |
| `[("...")]` | Data store / file | `XLSX[("source.xlsx")]` |
| `subgraph` | Logical grouping | `subgraph MLAI` |

> 💬 **RU:** GitHub Mermaid не поддерживает цвета нод natively — цветовая маркировка только в Excel diff_report. Круглые скобки `((" "))` — cylinder notation для файлов/БД.

---

## Arrow Types

| Arrow | Meaning |
|-------|---------|
| `-->` | Data or control flow (direction of processing) |

**sequenceDiagram:**
| Syntax | Meaning |
|--------|---------|
| `->>` | Synchronous call |
| `-->>` | Return |
| `opt` | Optional path |

> 💬 **RU:** Сплошная стрелка — основной flow. В sequenceDiagram opt block — pass-2 refinement (conditional). Нет async/queue arrows — система synchronous.

---

## Excel Diff Colors (not Mermaid)

| Status | Fill | Meaning |
|--------|------|---------|
| BOTH_DIFF | red FFCCCC | Расходятся quadrant и block |
| QUADRANT_DIFF | orange FFCC99 | Только quadrant |
| BLOCK_DIFF | yellow FFFF99 | Только block |

> 💬 **RU:** Цвета из `compare_and_update.py` → sheet «Расхождения». Используйте для приоритизации rule tuning — BOTH_DIFF первые в очереди.

---

## Component Naming Map

| Diagram label | Code entity |
|---------------|-------------|
| `rules.py` | Rule engine module |
| `SemanticIndex` | Embedding + prototype classifier |
| `TechRadarClassifier` | Orchestrator |
| `evaluate.py` | Data + metrics |
| `ensemble_weights.json` | Tuned weights |
| `prototypes.pkl` | Cached centroids |

> 💬 **RU:** При чтении диаграмм substituте label на file path из таблицы — так быстрее найти код.

---

## classification_method Values

| Value | Russian meaning |
|-------|-----------------|
| `rule_based` | Доминируют keywords/regex |
| `semantic` | Доминируют embeddings |
| `ensemble` | Смешение или conflict resolution |
| `default` | Fallback — нет scores |
| `semantic_inferred` | NN-Sputnik + semantic block path |

> 💬 **RU:** method в export Excel — быстрый фильтр для audit («покажи все semantic_inferred»). ensemble не always bad — may indicate legitimate ambiguity.

---

## Diagram Index

| Document | Type | Topic |
|----------|------|-------|
| executive-overview.md | flowchart LR | System context |
| architect/system-architecture.md | flowchart TD, LR | Components, batch |
| backend/pipeline.md | sequence, flowchart | Inference, retune |
| deep-dive-data-between-layers.md | flowchart LR | Transformations |
| ml-ai/architecture-position.md | flowchart LR | ML position |
| ml-ai/ranking-filtering.md | flowchart TD | Ranking steps |
| overview-architecture.md | flowchart TD | Onboarding simple |

> 💬 **RU:** Индекс всех Mermaid в docs — max 15 nodes per diagram rule observed. Если diagram не рендерится на GitHub — проверьте кавычки в labels с special chars и отсутствие C4 syntax.

---

**TODO:** Numbered figure references for PDF export.

> 💬 **RU:** TODO для будущей PDF версии docs — пока только GitHub markdown rendering.
