# ADR-0003: NN-Sputnik Training Exclusion and Runtime Block Inference

## Status

Accepted

> 💬 **RU:** Accepted — `exclude_nn_sputnik_rows` + `build_training_corpus` skip; runtime `raw_block` triggers warnings and content-based block prediction. Write policy in `update_source_xlsx.py` preserves metatag if block_conf < 0.5.

---

## Context

Many radar rows used placeholder block **«НН-Спутник. Вне КПМ»** instead of a real organizational block. Including this metatag as a training label would:

- teach prototypes a meaningless pseudo-class;
- distort block priors and compatibility matrices;
- inflate training row count without usable block signal.

Analysts still need block predictions for these rows when descriptions are filled.

Historical note: older `source.xlsx` had **1334** NN-Sputnik rows; manual markup in `source_16.06.xlsx` reduced this to **77** (remaining unresolved placeholders).

> 💬 **RU:** Context: NN-Sputnik — operational metatag «вне КПМ», not real block. Training on it poisoned block layer in iteration 2–3 (block macro F1 distorted). Manual markup resolved most rows with real blocks — corpus grew 1266→2523. Remaining 77 still need runtime inference path.

---

## Decision

1. **Training:** exclude any row where `is_nn_sputnik_block(block)` is True (`NN_SPUTNIK_PATTERNS` in `rules.py`).
2. **Inference:** when `raw_block` is NN-Sputnik:
   - predict block from text only;
   - add warnings `block inferred (source: НН-Спутник)`;
   - set method `semantic_inferred` when block path is semantic-dominated.
3. **Write-back:** in `update_source_xlsx.py`, if `block_conf < 0.5`, keep original NN-Sputnik block value (do not overwrite with low-confidence guess).

`canonical_block()` returns `None` for NN-Sputnik — row absent from training corpus but present in full Excel export.

> 💬 **RU:** Decision — three policies train/infer/write. Exclusion — hard filter in load_dataset. Inference — always pass raw_block from Excel in batch. Write threshold 0.5 — conservative; raise only with measured precision on hold-out. canonical_block None — prevents accidental use as label in corpus builder.

---

## Consequences

### Positive

- Cleaner block prototypes and priors.
- Explicit warnings flag rows needing human review.
- Conservative write policy avoids corrupting source with bad blocks.

### Negative / trade-offs

- Block confidence often lower for NN-Sputnik rows — more manual review.
- Training corpus no longer 1:1 with full Excel row count.

### Follow-up

- Continue resolving NN-Sputnik rows in manual markup (`source_16.06.xlsx`).
- Track count via `[load_dataset] Исключено N записей` log line.

> 💬 **RU:** Follow-up: каждый resolved NN-Sputnik row in manual markup improves corpus — rerun rebuild+retune. Low block conf on remaining 77 — expected; enrich descriptions in batch_markup. Log line count — sanity check after Excel edits.

---

## Alternatives considered

| Alternative | Why rejected |
|-------------|--------------|
| Train «NN-Sputnik» as its own block class | Not a valid business block; harms inference for real blocks |
| Always overwrite block on write | Risky at low confidence |
| Exclude rows entirely from inference | Products still appear in radar export pipelines |
| Map metatag to default block | Hides need for real assignment |

> 💬 **RU:** Own class rejected — metatag not in BLOCK_LABELS by design. Always overwrite caused bad blocks in early batch runs. Exclude from inference breaks reclassify_batch for 1334 rows — unacceptable.

---

## References

- Code: `rules.py` — `NN_SPUTNIK_PATTERNS`, `is_nn_sputnik_block`
- Code: `evaluate.py` — `exclude_nn_sputnik_rows`
- Code: `classifier.py` — `classify()` warnings
- Code: `scripts/update_source_xlsx.py` — write threshold
- Docs: [../architect/data-contracts.md](../architect/data-contracts.md)

> 💬 **RU:** grep `is_nn_sputnik_block` across repo when changing policy — touch evaluate, semantic, classifier, scripts consistently.
