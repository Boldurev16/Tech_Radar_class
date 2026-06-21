# ML Models

Models in use, I/O contracts, inference paths, quality and monitoring.

> 💬 **RU:** Список всех «моделей» в проекте — HF embedding + derived prototypes + rule engine (deterministic). Нет fine-tuned neural classifier head. Retrain = rebuild prototypes + optional weight grid search, not gradient descent on labels.

---

## Models in Use

| Model | Type | Purpose | Location |
|-------|------|---------|----------|
| `paraphrase-multilingual-mpnet-base-v2` | Sentence embedding | Primary encoder | `semantic.DEFAULT_MODEL` |
| `paraphrase-multilingual-MiniLM-L12-v2` | Sentence embedding | Fallback | `semantic.FALLBACK_MODEL` |
| Class prototypes | Mean pooling | Nearest-class inference | `models/prototypes.pkl` |
| Rule engine | Deterministic | High-precision patterns | `rules.py` |

**Not used:** LLM, cross-encoder reranker, fine-tuned classification head, external embedding API.

> 💬 **RU:** mpnet-base-v2 — multilingual, suited for RU+EN radar text. Fallback MiniLM smaller/faster but different space — if triggered, rebuild prototypes. Rule engine not a neural model but equally important for accuracy on keyword-clear scenarios (LLM, blockchain, SCADA).

---

## Sentence Transformer

### Loading

Lazy load on first `encode()` via `SentenceTransformer(model_name)`.

> 💬 **RU:** First encode downloads weights from HuggingFace — needs network unless cached in `~/.cache/huggingface`. Warm up model in long batch jobs once at start — reuse classifier instance.

### Inference Path

| Step | Input | Output |
|------|-------|--------|
| Encode | `list[str]` | L2-normalized ndarray |
| Compare | query vs prototypes | cosine scalar per label |
| Normalize | clip + sum | pseudo-probability |
| Select | sort | top-k tuples |

Batch/online: same code; batch jobs loop `classify()` — no cross-row batching optimization.

> 💬 **RU:** No GPU requirement but torch uses CUDA if available. encode batch size 1 in classify loop — performance bottleneck for 2600 rows. Future: batch encode in classify_batch — TODO not implemented.

---

## Prototype Construction (Offline)

Per label: collect training texts → mean embedding → store in pickle.

Empty class: fallback embed `[label]` string only.

> 💬 **RU:** Prototypes quality = training text diversity per class. Rare classes with 1–2 examples — weak centroids. Manual markup expansion dramatically improved block prototypes (corpus 1266→2523).

---

## Ensemble (Non-Neural)

Weighted fusion + multiplicative priors — see [ranking-filtering.md](ranking-filtering.md).

Tuned grid 0.1–0.9 in `optimize_ensemble_weights()`.

> 💬 **RU:** Ensemble not learned end-to-end — grid search on val macro F1. Separate quadrant/block weights reflect different error profiles (block F1 lower). JSON stores validation metrics for audit trail.

---

## Quality Metrics (Reference)

From `ensemble_weights.json` (manual corpus, test n=487):

| Metric | Value |
|--------|-------|
| quadrant macro F1 | 0.677 |
| block macro F1 | 0.548 |
| joint accuracy | 0.669 |
| quadrant accuracy | 0.760 |
| block accuracy | 0.875 |

> 💬 **RU:** Metrics post-retune on manual reference — use as internal baseline, not production SLA. Block macro F1 depressed by rare classes with 0 test support. Track joint accuracy and per-product spot checks for business acceptance.

---

## Monitoring Gaps

| Concern | State |
|---------|--------|
| Production logging | Console/script output only |
| Model version | `model_name` in pickle only |
| Drift detection | None — TODO periodic eval |
| Confidence calibration | Heuristic — not calibrated |
| Low-confidence tracking | `output/low_confidence_records.csv` |

> 💬 **RU:** No MLflow/W&B integration. Drift: rerun `retune_from_manual.py` + compare metrics JSON after each manual markup drop. Low-conf CSV — primary human review queue after auto update.

---

## Retrain Procedure

```bash
python semantic.py --rebuild
python scripts/retune_from_manual.py
python classifier.py --evaluate --stratify=multi
pytest tests/test_classifier.py
```

> 💬 **RU:** Standard retrain runbook. Order: rebuild prototypes on current source → retune weights on manual xlsx → evaluate hold-out → pytest boundary cases. Full corpus rebuild after retune recommended (see `prototypes_trained_on` in weights JSON). Budget ~15–20 min CPU time.

---

## Improvement Levers

1. More labeled data for rare quadrant/block pairs.
2. Keywords / disambiguation for systematic errors (`output/diff_report.xlsx`).
3. Adjust `ensemble_weights.json`.
4. Replace embedding model (full rebuild required).
5. **Future:** cross-encoder reranker on top-5 — not implemented.

> 💬 **RU:** Levers ordered by cost: rules cheapest, embedding model change most expensive. diff_report «Расхождения» sheet — prioritized rule tuning backlog. Cross-encoder — requires new ADR and training pipeline.
