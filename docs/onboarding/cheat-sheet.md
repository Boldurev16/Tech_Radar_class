# Cheat Sheet

> 💬 **RU:** Шпаргалка для быстрого старта. Прочитайте за 10 минут, затем откройте `classifier.py` и запустите pytest. Все пути относительно папки `Tech_Radar_class/`.

---

## What Is This?

Двухуровневый классификатор сценариев **Technology Radar**:
- **quadrant** — технологическое направление (24 класса);
- **block** — блок бизнес-процессов (16 классов).

Вход: **name** + **description** (+ опционально **ring**, **raw_block**).

> 💬 **RU:** Это не общий NLP-классификатор, а система с фиксированной таксономией НЛМК radar. Каждый сценарий получает две метки и confidence. При низком confidence нужна ручная проверка — автоматика не infallible.

---

## Project Layout

```
Tech_Radar_class/
├── classifier.py      ← начать здесь (главный API)
├── rules.py           ← keywords, правила, labels
├── semantic.py        ← embeddings + prototypes
├── evaluate.py        ← данные, метрики, export
├── data/
│   ├── source.xlsx              ← рабочий radar
│   └── source_16.06.xlsx        ← эталон ручной разметки
├── models/
│   ├── ensemble_weights.json    ← веса rule vs semantic
│   └── prototypes.pkl           ← центроиды embeddings
├── scripts/           ← CLI-утилиты
├── tests/             ← pytest
├── output/            ← отчёты, batch markup
└── docs/              ← документация
```

> 💬 **RU:** Структура flat — нет пакета `src/`. Core logic в четырёх `.py` в корне. `models/` — бинарные/json артефакты; без них классификатор медленно стартует или retune. `data/source_backup*.xlsx` — backups перед destructive scripts.

---

## First Files to Read

1. `classifier.py` — `ClassificationResult`, `TechRadarClassifier.classify()`
2. `rules.py` — `QUADRANT_LABELS`, `BLOCK_LABELS`, keywords
3. `evaluate.py` — `load_dataset()`
4. `tests/test_classifier.py` — 4 boundary-примера ожидаемого поведения

> 💬 **RU:** Читайте в этом порядке. Tests показывают «контракт» поведения (Erudit → LLM quadrant, переводчик → Apparat block). После изменения rules всегда гоняйте pytest — 6 тестов, ~10 сек.

---

## Quick Start

```bash
cd Tech_Radar_class
pip install -r requirements.txt
pytest tests/test_classifier.py -q
python scripts/spot_check.py --records "Directum,PlanDesigner"
```

> 💬 **RU:** Установка deps включает torch и sentence-transformers — первый pip install долгий. `-X utf8` на Windows для кириллицы в консоли. spot_check требует descriptions в batch_markup для NN-Sputnik продуктов — иначе weak predictions.

---

## Python API

```python
from classifier import TechRadarClassifier

clf = TechRadarClassifier(rebuild_prototypes=False)
result = clf.classify(
    "Directum",
    description="Платформа электронного документооборота...",
    ring="Перспективные Российские технологии",
    raw_block="НН-Спутник. Вне КПМ",
)
print(result.quadrant, result.quadrant_confidence)
print(result.warnings)
```

> 💬 **RU:** `rebuild_prototypes=False` — используйте cached pickle. Передавайте ring и raw_block как в source — иначе результат не совпадёт с batch pipeline. warnings — первое место для диагностики (low confidence, NN-Sputnik, layer conflict).

---

## Common Scripts

| Задача | Команда |
|--------|---------|
| Rebuild embeddings | `python semantic.py --rebuild` |
| Запись в source | `python scripts/update_source_xlsx.py` |
| Merge ручной разметки | `python scripts/compare_and_update.py` |
| Retune весов | `python scripts/retune_from_manual.py` |
| Batch reclassify | `python scripts/reclassify_batch.py --output output/batch_markup_v4.xlsx` |

> 💬 **RU:** Не путайте update_source (auto wins) и compare_and_update (manual wins). Перед любым save в source.xlsx закройте файл в Excel. retune ~13 мин на CPU. rebuild prototypes после смены разметки обязателен.

---

## Documentation Routes

| Роль | Куда идти |
|------|-----------|
| Новичок | [overview-architecture.md](overview-architecture.md) |
| Архитектор | [../architect/executive-overview.md](../architect/executive-overview.md) |
| Backend / pipeline | [../backend/pipeline.md](../backend/pipeline.md) |
| ML | [../ml-ai/ranking-filtering.md](../ml-ai/ranking-filtering.md) |

> 💬 **RU:** Документация на английском с русскими комментариями 💬 — кроме onboarding, где основной текст русский. ADR в `decisions/` фиксируют архитектурные решения — читайте перед крупными refactor.

---

## Gotchas

- Закрывайте Excel перед записью в `source.xlsx`.
- В batch всегда передавайте `ring`.
- NN-Sputnik исключён из обучения — block inferenced at runtime.
- HTTP API нет — только library + CLI.

> 💬 **RU:** Типичные инциденты: PermissionError (файл открыт), missing ring (wrong quadrant), stale prototypes (не rebuild после manual update). Нет Docker/K8s deploy — локальный Python batch.

---

## Downstream: куда уходит Excel

| Шаг | Что происходит | Кто отвечает |
|-----|----------------|--------------|
| 1 | Python записывает результат в `output/*.xlsx` | Python pipeline |
| 2 | Файл копируется в сетевую папку Windows | IT / оператор |
| 3 | Оператор отправляет письмо через Outlook → триггер RPA | Оператор / автоматизация |
| 4 | RPA-робот загружает файл в SiglaVision | RPA-команда |
| 5 | SiglaVision рендерит дашборд | BI-команда |

> 💬 **RU:** Если дашборд не обновился — не меняй Python-код сразу. Сначала проверь шаги 2–4: файл в share, письмо отправлено, RPA отработал. Любое изменение структуры output Excel (колонки, листы) согласуй с RPA и BI заранее. Подробнее: [overview-architecture.md](overview-architecture.md), [../backend/pipeline.md](../backend/pipeline.md#downstream-failure-scenarios).
