# ADR-NNNN: Title

## Status

Proposed | Accepted | Deprecated | Superseded by ADR-XXXX

> 💬 **RU:** Укажите текущий статус решения. Accepted — уже в коде. Proposed — на review. Deprecated — не использовать, но история важна. Superseded — заменено другим ADR (укажите номер).

---

## Context

Describe the problem, constraints, and symptoms that require a decision.

- What requirements or constraints exist?
- What metrics, incidents, or tech debt triggered this?
- Who is affected?

> 💬 **RU:** Context — «почему вообще возник вопрос». Опишите бизнес или технический pain: низкий F1, PermissionError, conflict между rule и semantic, требование сохранить Excel styles. Без context Decision выглядит arbitrary для future readers.

---

## Decision

State what was decided — concretely and verifiably.

- Which modules/files are affected?
- What behavior is expected after implementation?

> 💬 **RU:** Decision — одно чёткое предложение + bullets с files. Должно быть testable: «pass-2 не меняет label» → test Directum + pytest. Избегайте vague «улучшим качество» без mechanism.

---

## Consequences

### Positive

- …

### Negative / trade-offs

- …

### Follow-up

- …

> 💬 **RU:** Consequences — честные trade-offs. Positive без negative — red flag. Follow-up: TODO metrics, monitoring, docs updates. Если decision increases manual review load — say so.

---

## Alternatives considered

| Alternative | Why rejected |
|-------------|--------------|
| Option A | … |
| Option B | … |

> 💬 **RU:** Alternatives — что рассматривали и почему отвергли. Помогает не reopen settled debates. «Single multiclass model» vs «two-level» — classic example for this project.

---

## References

- Code: `path/to/file.py`
- Docs: `docs/...`
- Metrics: `results/...`

> 💬 **RU:** References — ссылки на code lines, metrics JSON, PR/issue if any. Минимум один path в repo — иначе ADR hard to validate.
