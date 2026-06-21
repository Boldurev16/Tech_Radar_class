# Tech Radar Classifier — Documentation

Two-level classifier for Technology Radar scenarios: given `name` + `description` (and optional `ring`, `raw_block`), predicts **quadrant** (24 classes) and **block** (16 classes). Implementation is a Python library and CLI scripts — **no HTTP API** in this repository.

> 💬 **RU:** Это официальная точка входа в документацию проекта. Система автоматически размечает сценарии Technology Radar по двум осям — технологическому направлению (quadrant) и блоку бизнес-процессов (block). Проект работает как Python-библиотека и набор CLI-скриптов, без веб-сервера. Начните с таблицы модулей ниже, затем выберите маршрут чтения под свою роль.

---

## Module Map

| Module | Path | Purpose |
|--------|------|---------|
| Classifier orchestrator | `classifier.py` | `TechRadarClassifier`, ensemble merge, ring prior, `ClassificationResult`, CLI |
| Rule layer | `rules.py` | Keywords, priority regex, disambiguation, label canonicalization, NN-Sputnik filter |
| Semantic layer | `semantic.py` | Sentence embeddings, class prototypes, `SemanticIndex` |
| Evaluation & I/O | `evaluate.py` | Dataset loading, metrics, stratified split, Excel export, weight tuning |
| Unit tests | `tests/test_classifier.py` | Boundary-case regression tests |
| Ensemble weights | `models/ensemble_weights.json` | Rule vs semantic weights (quadrant/block separately) |
| Prototype cache | `models/prototypes.pkl` | Pickled embedding centroids per class |
| Primary data | `data/source.xlsx` | Technology Radar workbook (sheet «Build your Technology Radar») |
| Manual reference | `data/source_16.06.xlsx` | Gold-standard manual markup for merge/retune |
| Batch reclassify | `scripts/reclassify_batch.py` | Reclassify `output/batch_markup*.xlsx` |
| Source update | `scripts/update_source_xlsx.py` | Write predictions to `source.xlsx` via openpyxl |
| Manual merge | `scripts/compare_and_update.py` | Diff report + manual-over-auto merge |
| Weight retune | `scripts/retune_from_manual.py` | Prototype rebuild + grid search weights |
| Spot check | `scripts/spot_check.py` | Point-check records by product name |
| Metrics artifacts | `results/*.json` | Hold-out and retune metrics |
| Batch outputs | `output/*.xlsx`, `output/*.csv` | Markup, diff, low-confidence reports |
| Demo notebook | `demo.ipynb` | Interactive examples |
| Dependencies | `requirements.txt` | Python packages |

> 💬 **RU:** Таблица связывает каждый модуль с его реальным путём в репозитории. `classifier.py` — главная точка входа для inference; `rules.py` и `semantic.py` — два независимых слоя классификации, которые оркестратор объединяет. Скрипты в `scripts/` — операционные задачи (запись в Excel, merge, retune). Артефакты в `models/` (`ensemble_weights.json`, `prototypes.pkl`) критичны: без них классификатор либо использует дефолтные веса, либо пересобирает прототипы при первом запуске (долго). При onboarding первым делом откройте `classifier.py` и `tests/test_classifier.py`.

---

## Reading Order by Role

### Architect
1. [architect/executive-overview.md](architect/executive-overview.md)
2. [architect/system-architecture.md](architect/system-architecture.md)
3. [architect/data-contracts.md](architect/data-contracts.md)

### Backend engineer
1. [backend/system-architecture.md](backend/system-architecture.md)
2. [backend/pipeline.md](backend/pipeline.md)
3. [backend/deep-dive-data-between-layers.md](backend/deep-dive-data-between-layers.md)

### ML / AI engineer
1. [ml-ai/architecture-position.md](ml-ai/architecture-position.md)
2. [ml-ai/metadata-filtering.md](ml-ai/metadata-filtering.md)
3. [ml-ai/ranking-filtering.md](ml-ai/ranking-filtering.md)
4. [ml-ai/ml-models.md](ml-ai/ml-models.md)

### New team member
1. [onboarding/cheat-sheet.md](onboarding/cheat-sheet.md)
2. [onboarding/overview-architecture.md](onboarding/overview-architecture.md)
3. [onboarding/diagram-legends-index.md](onboarding/diagram-legends-index.md)

> 💬 **RU:** Маршруты чтения разделены по ролям, чтобы не читать всё подряд. Архитектору важны границы системы и контракты данных; backend-инженеру — pipeline и передача структур между слоями; ML-инженеру — ranking, метаданные и модели. Новичку начните с onboarding — там текст на русском и минимум терминологии. Если вы правите классификацию конкретного продукта — параллельно держите открытым `scripts/spot_check.py` и `ml-ai/ranking-filtering.md`.

---

## Full Document Index

| Path | Audience |
|------|----------|
| [architect/executive-overview.md](architect/executive-overview.md) | Architect |
| [architect/system-architecture.md](architect/system-architecture.md) | Architect |
| [architect/data-contracts.md](architect/data-contracts.md) | Architect |
| [backend/system-architecture.md](backend/system-architecture.md) | Backend |
| [backend/pipeline.md](backend/pipeline.md) | Backend |
| [backend/deep-dive-data-between-layers.md](backend/deep-dive-data-between-layers.md) | Backend |
| [ml-ai/architecture-position.md](ml-ai/architecture-position.md) | ML/AI |
| [ml-ai/metadata-filtering.md](ml-ai/metadata-filtering.md) | ML/AI |
| [ml-ai/ranking-filtering.md](ml-ai/ranking-filtering.md) | ML/AI |
| [ml-ai/ml-models.md](ml-ai/ml-models.md) | ML/AI |
| [onboarding/cheat-sheet.md](onboarding/cheat-sheet.md) | Onboarding |
| [onboarding/overview-architecture.md](onboarding/overview-architecture.md) | Onboarding |
| [onboarding/diagram-legends-index.md](onboarding/diagram-legends-index.md) | Onboarding |
| [decisions/README.md](decisions/README.md) | All |
| [decisions/template-adr.md](decisions/template-adr.md) | All |
| [decisions/0001-two-level-classification.md](decisions/0001-two-level-classification.md) | All |
| [decisions/0002-rule-semantic-ensemble.md](decisions/0002-rule-semantic-ensemble.md) | All |
| [decisions/0003-nn-sputnik-handling.md](decisions/0003-nn-sputnik-handling.md) | All |
| [decisions/0004-rpa-trigger-via-outlook.md](decisions/0004-rpa-trigger-via-outlook.md) | All |

> 💬 **RU:** Полный индекс всех markdown-файлов в `docs/`. ADR-файлы в `decisions/` фиксируют ключевые архитектурные решения с обоснованием — при спорных изменениях сначала проверьте, не противоречите ли существующему ADR. Если добавляете новый паттерн (например, REST API) — создайте новый ADR по шаблону `template-adr.md`.

---

## Quick Module Index

| Question | Start here |
|----------|------------|
| How to call the classifier? | `classifier.py` → `TechRadarClassifier.classify()` |
| Where are keywords and rules? | `rules.py` |
| Where are embeddings? | `semantic.py` → `SemanticIndex` |
| How to load the dataset? | `evaluate.py` → `load_dataset()` |
| How to retune weights? | `scripts/retune_from_manual.py` |
| How to update Excel? | `scripts/update_source_xlsx.py` |

> 💬 **RU:** Быстрый указатель «где что искать в коде». Типичная ошибка новичка — править keywords в `classifier.py` (там их нет) вместо `rules.py`. Retune весов и rebuild прототипов — разные операции: retune меняет только `ensemble_weights.json`, rebuild — `prototypes.pkl`. После изменения `rules.py` retune не обязателен; после изменения разметки в Excel — нужны rebuild и/или retune.
