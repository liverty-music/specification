## Why

When a user signs up, the `user.created` event triggers an email verification via Zitadel — but if delivery fails (e.g. Postmark rate limit), no structured error log is emitted by the infrastructure layer, and the failed message is silently moved to the Poison Queue with no alerting. This makes it impossible to detect, diagnose, or recover from email delivery failures in production.

## What Changes

- **Add** structured logging to `EmailVerifier.SendVerification` and `EmailVerifier.ResendVerification` (backend) — success and error outcomes must be observable
- **Add** Poison Queue consumer in the backend event consumer app — messages routed to the Poison Queue must be logged at ERROR level so existing alert policies fire
- **Add** Poison Queue monitoring alert in cloud-provisioning — a dedicated Cloud Monitoring alert for NATS `POISON` stream message accumulation

## Capabilities

### New Capabilities

- `consumer-poison-queue-alerting`: Covers detection and alerting when messages are routed to the Poison Queue, including a consumer that emits ERROR logs and a Cloud Monitoring alert on POISON stream lag.

### Modified Capabilities

- `email-verification`: The `SendVerification` and `ResendVerification` infrastructure calls must emit structured INFO (success) and ERROR (failure) log entries. This is a requirement change — the existing spec does not mandate observability at the infrastructure layer call site.

## Impact

- **backend**: `internal/infrastructure/zitadel/email_verifier.go` — add logger calls; new `internal/adapter/event/poison_consumer.go` handler; wire into `internal/di/consumer.go`
- **cloud-provisioning**: `src/gcp/components/monitoring.ts` — add Poison Queue lag alert policy
- **NATS**: The existing `POISON` stream gains a consumer subscription for logging purposes (does not re-process messages)
