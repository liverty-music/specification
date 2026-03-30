## Context

The `email-verification` change implemented the `user.created → SendVerification` pipeline. A production incident revealed that when Postmark hit its free-tier rate limit, the Zitadel `SendEmailCode` call failed silently: no error was logged at the `EmailVerifier` level, the message was retried 3 times by Watermill, then routed to the `POISON` NATS stream with no further alerting. The POISON stream currently has 218 accumulated messages and zero consumers.

The existing `app-error-log-alerting` spec covers ERROR-level log alerting per workload, but that only fires if an ERROR is actually emitted. The gap is twofold:

1. `EmailVerifier` does not log at the call site — errors bubble silently through `UserConsumer` and into Watermill's retry/poison machinery.
2. No consumer reads from the `POISON` stream, so poison queue accumulation never triggers the existing alert policies.

## Goals / Non-Goals

**Goals:**
- Make `EmailVerifier.SendVerification` and `ResendVerification` observable: emit structured INFO on success, ERROR on failure, at the infrastructure layer call site
- Make Poison Queue accumulation detectable: add a consumer that emits ERROR logs for every poisoned message so existing workload alert policies fire
- Add a Cloud Monitoring alert for NATS `POISON` stream lag as a secondary safety net

**Non-Goals:**
- Re-processing or replaying Poison Queue messages (dead-letter redelivery is out of scope)
- Changing retry configuration or Watermill middleware
- Frontend changes
- Postmark plan upgrade (operational, not code)

## Decisions

### Decision 1: Log at the infrastructure layer, not the use-case layer

**Chosen**: Add `logger` calls inside `EmailVerifier.SendVerification` / `ResendVerification` in `internal/infrastructure/zitadel/email_verifier.go`.

**Alternatives considered**:
- Log only in `UserConsumer.Handle` — already done (`"sending email verification"` log exists), but the call site result is invisible. The infrastructure layer owns the external I/O and should own the observability.
- Log in both — redundant; the consumer already logs "sending", so the infra layer logs the outcome (success/failure).

**Rationale**: Consistent with how other infrastructure clients (DB, MusicBrainz) are instrumented. Keeps the use-case layer clean.

---

### Decision 2: Poison Queue consumer emits ERROR logs, does not re-process

**Chosen**: Add a `PoisonConsumer` handler that reads each message from the `POISON` stream, logs it at ERROR level with the original topic and error context, and acks it.

**Alternatives considered**:
- Cloud Monitoring metric-based alert on NATS stream message count — possible but requires exposing NATS metrics to Cloud Monitoring (not yet set up); the log-based approach reuses existing infrastructure.
- Re-processing logic (retry the original handler) — complex, risky; out of scope for this change.

**Rationale**: The existing `app-error-log-alerting` spec fires on any ERROR log from the consumer workload. A PoisonConsumer that logs ERROR for each dead-lettered message integrates with zero new alerting infrastructure. It also gives a permanent audit trail in Cloud Logging.

---

### Decision 3: Add a secondary NATS lag alert in cloud-provisioning

**Chosen**: Add a Cloud Monitoring log-based alert that triggers when the POISON stream consumer lag exceeds 0 (i.e., any unprocessed poisoned message). This fires even if the PoisonConsumer is down.

**Rationale**: Defense in depth. The PoisonConsumer alert requires the consumer Pod to be running. A NATS monitoring-based alert catches poison messages that accumulate when the consumer is scaled to zero (KEDA).

## Risks / Trade-offs

- **PoisonConsumer generates noise during incidents**: If a handler fails repeatedly for a legitimate transient reason (e.g., Postmark downtime), the POISON stream fills and the PoisonConsumer will emit many ERROR logs, triggering repeated alerts. Mitigation: the existing 12-hour notification rate limit on the alert policy suppresses duplicate Slack messages.

- **KEDA scale-to-zero delays PoisonConsumer**: The consumer Pod is subject to the same KEDA scale-to-zero behaviour as other handlers. If the consumer is down when a message is poisoned, the NATS lag alert (Decision 3) provides coverage.

- **POISON stream backlog (218 messages)**: On first deploy, the PoisonConsumer will process and log 218 existing messages as ERROR, triggering alerts. These are historical failures. Mitigation: drain or purge the POISON stream before deploying, or temporarily suppress alerts.

## Migration Plan

1. Add `logger` calls to `EmailVerifier` (backend) — no config change required
2. Implement `PoisonConsumer` and wire into `consumer.go` — adds a new NATS consumer on the `POISON` stream
3. Purge or acknowledge the 218 existing POISON messages before deploying (to avoid alert storm)
4. Deploy backend consumer — PoisonConsumer begins reading new poisoned messages
5. Add NATS lag alert in cloud-provisioning — deploy via Pulumi

**Rollback**: Remove `PoisonConsumer` handler registration from `consumer.go`. The alert policy can be deleted via Pulumi. No data is affected.

## Open Questions

- Should the existing 218 POISON messages be purged before deploy, or individually triaged? (operational decision, not a blocker)
- Should `PoisonConsumer` parse the CloudEvent payload and log the original topic/subject for better context? (nice-to-have, can be done in the same PR)
