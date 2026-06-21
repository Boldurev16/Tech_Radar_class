# ADR-0004: RPA Trigger via Outlook Email

## Status

Accepted

> 💬 **RU:** Статус Accepted — действующий способ запуска RPA-робота в production downstream. Python pipeline не вызывает RPA API напрямую; триггер — исходящее письмо Outlook. При смене механизма (API, file watcher only) создайте новый ADR и обновите docs/architect и backend/pipeline.

---

## Context

After the Python pipeline generates an output Excel file (`output/*.xlsx`), data must reach **SiglaVision** for dashboard visualization. The path is:

1. File copied to a **Windows network share**.
2. **RPA robot** picks up the file and uploads to SiglaVision.
3. RPA start requires a **trigger** decoupled from Python — no direct Python ↔ RPA API integration exists in the repository.

Operators need a simple, auditable handoff without embedding RPA credentials or orchestration logic in the classifier codebase.

> 💬 **RU:** Context: downstream — share → RPA → SiglaVision. Python-команда не владеет RPA runtime. Нужен слабосвязанный триггер без hard dependency Python↔RPA SDK. Письмо Outlook даёт human-in-the-loop checkpoint (оператор подтверждает готовность файла) и audit trail в почте. Минус — ручной шаг или отдельная автоматизация отправки.

---

## Decision

Use an **outgoing Outlook email** as the RPA robot trigger signal.

- Python pipeline responsibility ends at producing valid output Excel and (operationally) placing it on the network share.
- **Operator or automation** sends the trigger email via Outlook after the file is available.
- RPA robot listens for the email trigger **and** reads the file from the network share before pushing to SiglaVision.

Evidence: documented in [executive-overview.md](../architect/executive-overview.md), [system-architecture.md](../architect/system-architecture.md), [pipeline.md](../backend/pipeline.md). **Not implemented in Python source** — external process.

> 💬 **RU:** Decision: email = trigger, not file appearance alone (both required per integration design). Python не шлёт письмо автоматически in-repo — TODO если нужна auto-send через win32com. Любая auto-send — отдельный script + security review. RPA team owns robot subscription to mailbox/rule.

---

## Consequences

### Positive

- No RPA SDK or credentials in Python repository.
- Clear operational checkpoint before dashboard refresh.
- Email provides audit trail (who/when triggered).

### Negative / trade-offs

- Manual step if operator forgets to send email → dashboard not updated.
- Depends on Outlook availability and mail routing rules.
- Two signals (file + email) must align — partial completion fails silently from Python’s view.

### Follow-up

- TODO: document exact mailbox, subject line, and RPA rule name.
- TODO: optional Python helper to send trigger email (requires ADR amendment).
- Coordinate output Excel schema changes with RPA and BI teams.

> 💬 **RU:** Consequences: простота интеграции vs operational risk «забыли письмо». Мониторинг — со стороны RPA/BI, не Python logs. Follow-up TODOs критичны для runbook — без subject line новичок не воспроизведёт trigger. Schema change без BI — #1 cause wrong dashboard data.

---

## Alternatives considered

| Alternative | Why rejected |
|-------------|--------------|
| Direct RPA API call from Python | Couples codebase to RPA platform; credentials in repo; outside team ownership |
| File watcher on network share only | No explicit human approval; harder to audit; robot may run on incomplete file |
| Scheduled task (time-based) | Not tied to pipeline completion; stale or duplicate runs |
| Message queue (Kafka/RabbitMQ) | No infrastructure in project; overkill for batch Excel pipeline |

> 💬 **RU:** Alternatives: API — правильно технически, но governance (RPA team owns robot). File-only watcher — риск race if copy slow. Cron — не sync с pipeline finish. Queue — нет infra. Email — pragmatic enterprise pattern для handoff между командами.

---

## References

- Docs: [../backend/pipeline.md](../backend/pipeline.md#downstream-failure-scenarios)
- Docs: [../architect/system-architecture.md](../architect/system-architecture.md#integration-layer)
- Docs: [../onboarding/overview-architecture.md](../onboarding/overview-architecture.md)

> 💬 **RU:** References — downstream sections added in same documentation pass. Code reference отсутствует intentionally (external integration). При добавлении Python mail helper — link script path here.
