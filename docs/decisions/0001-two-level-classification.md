# ADR-0001: Two-Level Quadrant-Then-Block Classification

## Status

Accepted

> 💬 **RU:** Статус Accepted — реализовано в `classifier.classify()`: сначала `_classify_quadrant`, затем `_classify_block(quadrant_hint=...)`. Менять порядок или объединять в один 40-class head без нового ADR нельзя.

---

## Context

Technology Radar scenarios require two hierarchical labels from different taxonomies:
- **Quadrant** — 24 technology domains.
- **Block** — 16 organizational / process blocks.

Joint single-class classification over 24×16 combinations would be sparse (most pairs never appear in training). Block choice often depends on technology domain (co-occurrence in historical data).

> 💬 **RU:** Context: две ортогональные оси radar, не flat multiclass. Sparse joint space — типичная проблема hierarchical classification. Historical co-occurrence block↔quadrant используется через compat matrices в `_merge_scores`. Business stakeholders think in two steps: «какая технология» → «какой блок».

---

## Decision

Implement **sequential two-level classification**:

1. Predict quadrant from `name` + `description` (+ ring metadata for post-rules).
2. Predict block using predicted quadrant as compatibility hint (`compat_q_b` row).

Optional pass-2 re-runs quadrant with `block_hint` but **must not change** the quadrant label (iteration 4 guard).

Evidence: `classifier.py` — `classify()` calls `_classify_quadrant` before `_classify_block`.

> 💬 **RU:** Decision фиксирует cascade architecture. quadrant_hint передаётся в block merge — ошибка quadrant cascades. Pass-2 guard (same label only) добавлен после bug Directum RU → integration flip via compat. При отладке всегда смотрите quadrant перед block.

---

## Consequences

### Positive

- Smaller effective label space per step.
- Compatibility matrices encode valid block↔quadrant pairs from training data.
- Independent ensemble weights per field (see ADR-0002).

### Negative / trade-offs

- Quadrant errors propagate to block prediction.
- Two merge pipelines to maintain and tune.

### Follow-up

- Monitor joint accuracy vs per-field accuracy on manual hold-out.

> 💬 **RU:** Trade-off cascade error — fundamental; mitigate via quadrant quality (rules, ring prior). Two pipelines — operational cost for ML team (separate weights retune). Follow-up: track joint accuracy in retune JSON already — watch trend after manual markup updates.

---

## Alternatives considered

| Alternative | Why rejected |
|-------------|--------------|
| Single 384-class joint classifier | Too sparse; insufficient examples per pair |
| Predict block first | Business taxonomy assumes technology-first radar layout |
| Independent parallel prediction | Ignores strong block↔quadrant co-occurrence in data |

> 💬 **RU:** Joint 384-class rejected из-за data sparsity — большинство пар never labeled. Block-first противоречит mental model analysts. Parallel без hint теряет compat signal — block F1 dropped in experiments (Status: inferred from compat matrix design).

---

## References

- Code: `classifier.py` — `classify()`, `_classify_quadrant`, `_classify_block`
- Docs: [../architect/data-contracts.md](../architect/data-contracts.md)
- Matrices: `evaluate.compatibility_matrix`, `block_quadrant_matrix`

> 💬 **RU:** References для code review: grep `_classify_quadrant` call order in classify(). Compat matrices rebuilt on init from `load_dataset` — change DATA_PATH changes matrices silently.
