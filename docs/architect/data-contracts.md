# Data Contracts

Source of truth: `evaluate.py`, `classifier.py` (`ClassificationResult`), `rules.py` (label lists), sheet «Build your Technology Radar» in `data/source.xlsx`.

> 💬 **RU:** Этот документ — canonical reference для структур данных. При изменении `ClassificationResult` или колонок Excel обновляйте этот файл и ADR при необходимости. Все поля ниже подтверждены чтением кода и `pd.read_excel` на `source.xlsx`.

---

## Excel: Sheet «Build your Technology Radar»

| Column | Required | Updated by classifier scripts | Description |
|--------|----------|------------------------------|-------------|
| `name` | yes | no | Scenario / product name (join key) |
| `type & category` | no | no | Radar category; **not used in classify()** |
| `ring` | no | no | TRL ring; input for ring prior |
| `quadrant` | yes | yes | Technology direction label |
| `block` | yes | yes | Business process block label |
| `description` | no | no | Scenario description text |

> 💬 **RU:** Колонка `name` — ключ для merge скриптов; в source 33 дубликата name (keep=last в scripts). `type & category` игнорируется классификатором — TODO: оценить predictive value. `ring` не пишется скриптами, но обязателен как input при batch classify. `quadrant`/`block` обновляются только через openpyxl cell write — стили других колонок сохраняются.

**Confirmed columns:** `['name', 'type & category', 'ring', 'quadrant', 'block', 'description']`

---

## Reference Sheets (Read-Only for Classifier)

| Sheet | Used by | Purpose |
|-------|---------|---------|
| `Quadrants` | Not imported in Python | Reference taxonomy |
| `Rings` | Not imported in Python | TRL reference |
| `Block` | `load_block_process_codes()` | Process codes → block score boost |
| `Table`, `Description`, `Circle` | Not referenced in Python | TODO: confirm with radar owners |

> 💬 **RU:** Только sheet `Block` влияет на inference (process codes в колонке «Процессы»). Остальные листы — справочники radar UI. Status: inferred для `Table`, `Description`, `Circle` — не найдены импорты в Python.

---

## Training Corpus (`load_dataset`)

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Scenario name |
| `description` | str | Description text |
| `text` | str | Normalized `"name \| description"` |
| `quadrant` | str | Canonical quadrant label |
| `block` | str | Canonical block label |
| `ring` | str | Ring value (may be empty) |

> 💬 **RU:** Training corpus формируется в `build_training_corpus` (`semantic.py`). Поле `text` — единственный input для embeddings. `ring` хранится в corpus, но **не** concatenated в `text` — ring влияет только через rule post-process в `classifier.py`. Filter: NN-Sputnik rows excluded; invalid canonical labels dropped.

**Filter rule:** `is_nn_sputnik_block(block) == True` → row excluded from training.

---

## API Contract: `ClassificationResult`

Defined in `classifier.py` as `@dataclass`:

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Input name echoed |
| `quadrant` | str | Predicted quadrant label |
| `block` | str | Predicted block label |
| `quadrant_confidence` | float | 0.0–1.0 |
| `block_confidence` | float | 0.0–1.0 |
| `quadrant_top3` | list[tuple[str, float]] | Top-3 quadrant scores |
| `block_top3` | list[tuple[str, float]] | Top-3 block scores |
| `classification_method` | str | See method values below |
| `warnings` | list[str] | Diagnostic strings |

> 💬 **RU:** `ClassificationResult` — единственный output DTO (не Pydantic/OpenAPI). `classification_method` объясняет, какой слой доминировал — полезно при отладке. `warnings` не fail inference: low confidence, NN-Sputnik, layer conflict записываются как строки. Confidence — heuristic max(rule, semantic, merged), не calibrated probability. Не используйте conf как strict probability threshold без validation на вашем hold-out.

### `classification_method` values

| Value | Meaning |
|-------|---------|
| `rule_based` | Rule layer dominated merge |
| `semantic` | Embedding layer dominated |
| `ensemble` | Mixed or conflict resolution |
| `default` | Fallback label (no scores) |
| `semantic_inferred` | NN-Sputnik row with semantic block path |

> 💬 **RU:** `semantic_inferred` — специфичный case для NN-Sputnik input когда block path semantic. `ensemble` часто означает conflict между rule top и semantic top — смотрите warning `layer_conflict`.

---

## `classify()` Inputs

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | yes | Scenario name |
| `description` | no (default `""`) | Description |
| `raw_block` | no | Original block from Excel; triggers NN-Sputnik handling |
| `ring` | no | TRL ring string |

> 💬 **RU:** Все четыре параметра важны для batch parity с training behavior. Omitting `ring` отключает disambiguation veto и ring prior — типичная причина расхождения spot_check vs production. `raw_block` нужен для NN-Sputnik warnings и write policy в `update_source_xlsx.py`.

---

## Label Vocabularies

### Quadrants (`QUADRANT_LABELS`, `rules.py` lines 8–33)

24 labels. Alias map: `QUADRANT_ALIASES` (typo fix for LLM quadrant name).

> 💬 **RU:** Quadrant labels — closed set. Новый quadrant требует добавления в `QUADRANT_LABELS`, keywords, rebuild prototypes. Typo «яхыковая модель» mapped через alias — при новых typos в source добавляйте в `QUADRANT_ALIASES`.

### Blocks (`BLOCK_LABELS`, `rules.py` lines 35–52)

16 labels. Aliases: `BLOCK_ALIASES`; fuzzy fallback via `normalize_block()` (threshold 0.72).

> 💬 **RU:** Block labels включают длинные официальные названия с `\u200b` zero-width chars — `BLOCK_ALIASES` их нормализует. Fuzzy match может mis-map редкие блоки — проверяйте `unmapped_blocks.csv` после load.

---

## NN-Sputnik Metatag

Patterns in `NN_SPUTNIK_PATTERNS`: `НН-Спутник`, `нн-спутnik`, `NN-Sputnik`, `Вне КПМ`.

| Context | Behavior |
|---------|----------|
| Training | Row skipped |
| Inference with `raw_block` | Block predicted from content; warnings added |
| `update_source_xlsx.py` | If `block_conf < 0.5`, keep original NN-Sputnik block |

> 💬 **RU:** NN-Sputnik — ключевое архитектурное решение (ADR-0003). ~77 rows in current manual file still carry metatag. При conf < 0.5 исходный block сохраняется — не перезаписывайте слепо. Для quality improvement заполните descriptions и real blocks в manual reference.

---

## Ensemble Weights Artifact

File: `models/ensemble_weights.json`

| Field | Current value | Description |
|-------|---------------|-------------|
| `optimized_weight_rule_quadrant` | 0.1 | Rule weight for quadrant merge |
| `optimized_weight_rule_block` | 0.3 | Rule weight for block merge |
| `source` | `source_16.06.xlsx` | Dataset used for last retune |
| `final_test_full_prototypes` | object | Hold-out metrics |

> 💬 **RU:** Weights tuned on manual corpus — semantic-heavy for quadrant (0.1 rule = 90% semantic base). После retune перезапустите `pytest` и spot_check на проблемных продуктах. File also stores metrics for audit — не удаляйте historical fields без migration note.

---

## Prototypes Artifact

File: `models/prototypes.pkl` (pickle)

| Key | Type | Description |
|-----|------|-------------|
| `model_name` | str | HF model id |
| `quadrant_prototypes` | dict[str, ndarray] | Centroid per quadrant |
| `block_prototypes` | dict[str, ndarray] | Centroid per block |

> 💬 **RU:** Pickle не versioned explicitly — при смене `model_name` in code обязателен `--rebuild`. Prototypes = mean embedding of training texts per class; empty class falls back to embedding of label string only. Binary artifact не diff-friendly — храните in git LFS or rebuild from source.

---

## Invariants

1. Canonical quadrant/block must be in `QUADRANT_LABELS` / `BLOCK_LABELS` after `canonical_*()`.
2. Confidence clipped to `[0, 1]` in `classify()`.
3. Pass-2 quadrant refinement never changes predicted quadrant label.
4. Manual markup from `source_16.06.xlsx` wins over auto in `compare_and_update.py`.

> 💬 **RU:** Invariant #3 добавлен в iteration 4 — без него compat matrix flip'ал Directum RU в integration. Invariant #4 — business rule: ручная разметка authoritative. Нарушение invariants при refactor — regression на `tests/test_classifier.py` и spot_check Directum/PlanDesigner.

---

## Versioning

| Artifact | Approach |
|----------|----------|
| Excel source | File backups (`source_backup*.xlsx`); no schema version field |
| `ensemble_weights.json` | Git + `source` field |
| `prototypes.pkl` | Rebuild via `semantic.py --rebuild` |

**TODO:** Add explicit `schema_version` to weights JSON and export files.

> 💬 **RU:** Versioning сейчас informal — только backup xlsx и git history. При team scale добавьте `schema_version` и changelog в `ensemble_weights.json`. TODO не блокирует текущую работу, но усложняет rollback после retune.
