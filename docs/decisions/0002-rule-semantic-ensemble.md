# ADR-0002: Rule + Semantic Ensemble with Separate Field Weights

## Status

Accepted

> 💬 **RU:** Accepted — `_merge_scores` combines rule dict and semantic top-k; weights loaded from `ensemble_weights.json` separately for quadrant and block. Current production values: quadrant rule 0.1, block rule 0.3 (post manual retune).

---

## Context

Keyword rules excel on explicit markers (LLM, blockchain, SCADA) but miss paraphrases. Sentence embeddings cover synonyms but blur similar domains (import substitution vs integration for ECM products).

A single global weight cannot optimize both quadrant (24 classes, semantic-heavy) and block (16 classes, more keyword structure).

> 💬 **RU:** Context: ни rule-only, ни semantic-only insufficient на full radar. Quadrant errors often lexical ambiguity; block errors often org-name keywords. Iteration 3 grid search showed different optimal rule fractions per field. Adaptive `_resolve_ensemble_weights` further modulates per sample by rule_conf.

---

## Decision

1. Maintain **two scoring layers**: `rules.score_labels` and `SemanticIndex.classify`.
2. Fuse via `_merge_scores` with:
   - separate `optimized_weight_rule_quadrant` and `optimized_weight_rule_block`;
   - adaptive overrides when rule_conf ≥ 0.8 or < 0.5;
   - class priors and compatibility row weighting on conflict/low-rule paths.
3. Tune weights by grid search on validation split (`optimize_ensemble_weights` in `evaluate.py`).

Persist results in `models/ensemble_weights.json`.

> 💬 **RU:** Decision — hybrid ensemble not stacking models. Grid search 0.1–0.9 on val split — not end-to-end learned. JSON artifact must deploy with code — mismatch old weights + new rules causes silent behavior change. After rule-heavy iteration 4, retune recommended (done on source_16.06).

---

## Consequences

### Positive

- Interpretable `classification_method` (rule vs semantic vs ensemble).
- Field-specific tuning improves quadrant without hurting block arbitrarily.

### Negative / trade-offs

- Grid search cost (~18 eval passes per retune).
- Adaptive rules interact with static JSON weights — hard to predict effective mix per sample.

### Follow-up

- TODO: document retune cadence when manual markup updates.

> 💬 **RU:** Consequence: debugging requires inspecting both layers + effective weights, not only JSON numbers. Retune ~13 min CPU — schedule after major markup drop. classification_method in export — use for error analysis dashboards (future).

---

## Alternatives considered

| Alternative | Why rejected |
|-------------|--------------|
| Rules only | Poor on paraphrases and long descriptions |
| Semantic only | Weak on rare classes; misses high-precision regex |
| Single shared weight | Suboptimal on hold-out vs separate weights |
| Learned stacking meta-classifier | No labeled meta-data; overkill for batch Excel pipeline |

> 💬 **RU:** Rules-only failed on description-rich NN-Sputnik rows. Semantic-only hurt keyword-clear cases (LLM, IoT). Meta-classifier needs more labels than available — rejected for scope.

---

## References

- Code: `classifier.py` — `_merge_scores`, `_resolve_ensemble_weights`
- Code: `evaluate.py` — `optimize_ensemble_weights`
- Artifact: `models/ensemble_weights.json`
- Script: `scripts/retune_from_manual.py`

> 💬 **RU:** Tune via retune_from_manual.py hardcoded on source_16.06.xlsx — change path if new gold file. weights JSON includes test metrics — compare before/after retune.
