## 1. Backend — EmailVerifier logging

- [x] 1.1 Add `logger *logging.Logger` field to `EmailVerifier` struct in `internal/infrastructure/zitadel/email_verifier.go`
- [x] 1.2 Update `NewEmailVerifier` to accept and store the logger (already passed as parameter — wire it into the struct)
- [x] 1.3 Add INFO log (`msg="email verification sent"`, `external_id`) on success in `SendVerification`
- [x] 1.4 Add ERROR log (`msg="failed to send email code"`, `external_id`) on error in `SendVerification`
- [x] 1.5 Add INFO log (`msg="email verification resent"`, `external_id`) on success in `ResendVerification`
- [x] 1.6 Add ERROR log (`msg="failed to resend email code"`, `external_id`) on error in `ResendVerification`
- [x] 1.7 Update unit tests in `email_verifier_test.go` to assert log output on success and failure paths

## 2. Backend — Poison Queue consumer

- [x] 2.1 Create `internal/adapter/event/poison_consumer.go` with a `PoisonConsumer` struct and `Handle` method
- [x] 2.2 `Handle` must parse the message UUID and metadata (original topic if available), emit ERROR log (`msg="message routed to poison queue"`, `topic`, `uuid`), and return nil (ack)
- [x] 2.3 Wire `PoisonConsumer` into `internal/di/consumer.go` — register handler on `messaging.PoisonQueueSubject`
- [x] 2.4 Add unit tests for `PoisonConsumer.Handle` covering the ERROR log assertion

## 3. Pre-deploy — POISON stream cleanup

- [x] 3.1 Purge the 218 existing messages from the NATS `POISON` stream in the dev environment before deploying (operational step — documented in `backend/tmp/purge-poison-stream.md`)

## 4. Backend — Deploy and verify

- [ ] 4.1 Run `make check` in backend repo (lint + tests pass)
- [ ] 4.2 Open backend PR, confirm CI passes
- [ ] 4.3 After merge, verify in Cloud Logging that `EmailVerifier` INFO logs appear for the next sign-up
- [ ] 4.4 Verify Poison Queue consumer ERROR log appears in Cloud Logging when a poisoned message is injected (manual test or trigger a known-failing message)

## 5. Cloud Provisioning — POISON stream lag alert

- [x] 5.1 Research how to surface NATS JetStream consumer lag as a Cloud Monitoring metric — decided to use log-based alert (reuses existing infra, no new metric pipeline needed)
- [x] 5.2 Add a log-based alert policy in `cloud-provisioning/src/gcp/components/monitoring.ts` that fires on consumer ERROR logs matching `"message routed to poison queue"`
- [ ] 5.3 Run `make lint` in cloud-provisioning, open PR, confirm CI passes
- [ ] 5.4 Run `pulumi preview` to confirm alert policy diff is correct
- [ ] 5.5 After merge, verify alert policy appears in GCP Cloud Monitoring console
