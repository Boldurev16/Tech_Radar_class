# Architecture Decision Records (ADR)

## What Is an ADR?

An ADR captures a significant architectural decision: context, choice, consequences, and rejected alternatives. Files live in `docs/decisions/`.

> 💬 **RU:** ADR — способ зафиксировать «почему так сделано», а не только «как». При споре в code review или при onboarding нового архитектора ADR быстрее, чем archaeology по git history. Новое решение, меняющее поведение classify pipeline — оформляйте ADR до merge.

---

## How to Read

1. Find the entry in the index below.
2. Check **Status** — only `Accepted` reflects current code.
3. If ADR conflicts with code, code is current until ADR is updated.

> 💬 **RU:** Status Accepted — действующее решение. Deprecated/Superseded — читайте для истории, не для implementation. Конфликт ADR vs code — bug либо в docs, либо unintentional regression; выясните через pytest и spot_check.

---

## How to Create

1. Copy [template-adr.md](template-adr.md) → `docs/decisions/NNNN-short-title.md`.
2. Fill all sections (English) + RU hint comments where applicable.
3. Add a row to the index on this page.
4. Link from affected docs (`docs/README.md`, pipeline, etc.).

> 💬 **RU:** Numbering NNNN sequential — следующий свободный после 0003. Slug в lowercase через дефис. После ADR обновите module map если меняются boundaries или contracts.

---

## Index

| ADR | Title | Status | Date | File |
|-----|-------|--------|------|------|
| ADR-0001 | Two-level quadrant-then-block classification | Accepted | 2026-06 | [0001-two-level-classification.md](0001-two-level-classification.md) |
| ADR-0002 | Rule + semantic ensemble with separate field weights | Accepted | 2026-06 | [0002-rule-semantic-ensemble.md](0002-rule-semantic-ensemble.md) |
| ADR-0003 | NN-Sputnik training exclusion and runtime block inference | Accepted | 2026-06 | [0003-nn-sputnik-handling.md](0003-nn-sputnik-handling.md) |
| ADR-0004 | RPA trigger via Outlook email | Accepted | 2026-06 | [0004-rpa-trigger-via-outlook.md](0004-rpa-trigger-via-outlook.md) |

> 💬 **RU:** **ADR-0001** — two-level classify. **ADR-0002** — ensemble weights. **ADR-0003** — NN-Sputnik. **ADR-0004** — downstream: Outlook email triggers RPA after Excel lands on network share; Python не управляет RPA. При инциденте «dashboard not updated» читайте ADR-0004 + pipeline Failure Scenarios.

---

## Superseded / Proposed

None at this time.

> 💬 **RU:** Когда решение заменяется — mark old ADR Superseded by ADR-XXXX, не удаляйте файл. Proposed — для review до implementation.

---

## Related Documents

- [../architect/system-architecture.md](../architect/system-architecture.md)
- [../backend/pipeline.md](../backend/pipeline.md)
- [../ml-ai/ml-models.md](../ml-ai/ml-models.md)

> 💬 **RU:** Related docs — canonical architecture text; ADR — rationale behind key choices referenced there.
