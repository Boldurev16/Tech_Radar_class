# Metadata Filtering

Metadata used in the pipeline: origin, normalization, and filtering effects.

> 💬 **RU:** Metadata — поля кроме текста сценария, влияющие на фильтрацию и post-processing. Главная ошибка batch pipeline — не передать `ring` и `raw_block`. Этот документ — checklist полей при интеграции нового data source.

---

## Metadata Inventory

| Field | Source column | Training | Inference | In embedding |
|-------|---------------|----------|-----------|--------------|
| `name` | `name` | yes | yes | yes |
| `description` | `description` | yes | yes | yes |
| `ring` | `ring` | stored | yes | **no** |
| `block` (raw) | `block` | filter + label | `raw_block` | **no** |
| `quadrant` (label) | `quadrant` | target | — | **no** |
| `type & category` | `type & category` | **no** | **no** | **no** |
| Process codes | sheet `Block` | block boost | block boost | **no** |

> 💬 **RU:** Только name и description попадают в embedding input (`text`). Ring влияет на disambiguation veto и RING_QUADRANT_PRIOR — без ring Directum RU ведёт себя иначе. raw_block триггерит NN-Sputnik path. type & category полностью ignored — potential future feature.

---

## Normalization Functions

| Function | File | Purpose |
|----------|------|---------|
| `normalize_text` | `rules.py` | lower, ё→е, whitespace |
| `normalize_ring` | `rules.py` | Map TRL variants to prior keys |
| `canonical_quadrant` | `rules.py` | Alias + label set membership |
| `canonical_block` | `rules.py` | Alias + fuzzy; None for NN-Sputnik |
| `is_nn_sputnik_block` | `rules.py` | Substring match on patterns |

> 💬 **RU:** normalize_ring collapses «Перспективные Российские …» variants — без этого prior keys miss. canonical_block returns None for NN-Sputnik — row excluded from training but still in full Excel export. Fuzzy block match can assign wrong canonical block — audit unmapped_blocks.csv.

---

## Training-Time Filtering

Exclusion chain in `build_training_corpus`: NN-Sputnik → invalid labels → empty name.

Current manual corpus: **77** NN-Sputnik excluded from **2600** rows → **2523** trainable.

> 💬 **RU:** Training filter определяет, какие rows строят prototypes. Resolving NN-Sputnik to real blocks in manual markup increased corpus ~2× vs iteration 3 — major quality shift. After bulk block assignment rerun rebuild + retune.

---

## Inference-Time Effects

### NN-Sputnik (`raw_block`)

Warnings added; block inferred. Write policy: keep original if `block_conf < 0.5`.

> 💬 **RU:** NN-Sputnik inference — block predicted from content only. Low conf → preserve metatag in source update — avoids wrong overwrite. Fill descriptions in batch_markup for better inference.

### Ring — disambiguation veto

СЭД rule: veto when ring = «Перспективные Российские технологии». BI rule: no veto.

> 💬 **RU:** Veto preserves import substitution for Russian ECM products (Directum RU). BI/PlanDesigner uses empty veto — integration even on RU ring. Test both when changing DISAMBIGUATION_RULES.

### Ring — quadrant prior (`RING_QUADRANT_PRIOR`)

| Ring | Effect |
|------|--------|
| Перспективные Российские технологии | +0.6 import if max_conf < 0.70 |
| Перспективные Мировые технологии | −0.3 import always |
| Внедряется | +0.05 conf boost |
| Прототипируется | +0.03 conf boost |

> 💬 **RU:** Prior applies after merge — can flip winner when max_conf below threshold. «Планируется к внедрению» has no entry in prior dict — passes through unchanged. Map more rings if business requires.

### Process codes

`apply_process_code_boost`: +0.25 block score if code substring in text.

> 💬 **RU:** Process codes parsed from Block sheet regex `[XX.N.N]`. Missing sheet or typo in code — silent no boost. Verify codes match scenario text language (often Russian descriptions, Latin codes).

---

## Gaps (Not Used)

| Metadata | Status |
|----------|--------|
| `type & category` | Ignored — TODO evaluate predictive value |
| `ring` in embeddings | Not concatenated to text |
| Gold quadrant at block step | Only predicted quadrant hint used |

> 💬 **RU:** Gaps — intentional or tech debt. Concatenating ring to text for embedding — experiment candidate. Using gold labels at eval only — predicted hint propagates errors quadrant→block.

---

## Debug Commands

```bash
python scripts/spot_check.py --records "Directum,PlanDesigner"
```

> 💬 **RU:** spot_check выводит Ring и warnings — первый шаг при «неправильный quadrant». Убедитесь descriptions merged from batch_markup (script does this if file exists). Compare ring value exact string to veto list in DISAMBIGUATION_RULES.

See [ranking-filtering.md](ranking-filtering.md).
