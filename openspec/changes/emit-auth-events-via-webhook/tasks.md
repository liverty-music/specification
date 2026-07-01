# Tasks

## 1. Zitadel `CreateSession` Actions v2 resources (cloud-provisioning)

- [ ] 1.1 Add a `ZitadelExecutionResponse` dynamic resource in `src/zitadel/dynamic/execution.ts` (condition `{ response: { method } }`), mirroring the existing `ZitadelExecutionRequest`. Only `function` and `request` conditions exist today; the `response` side is required by design Decision 1a.
- [ ] 1.2 In `src/zitadel/components/actions-v2.ts`, provision a new `CreateSession` Target the same way as `pre-access-token-webhook`: `targetType: 'REST_CALL'`, `payloadType: 'PAYLOAD_TYPE_JWT'` (so the backend verifies via its JWKS validator — no HMAC secret), and `interruptOnError: false` (analytics MUST NOT block login). Point its endpoint at the new backend webhook path.
- [ ] 1.3 Bind a `ZitadelExecutionResponse` on `/zitadel.session.v2.SessionService/CreateSession` to that Target.
- [ ] 1.4 Wire the new endpoint URL through `src/zitadel/index.ts` / `constants.ts` alongside `PRE_ACCESS_TOKEN_PATH`.

## 2. Backend `CreateSession` webhook handler

- [ ] 2.1 Add a handler in `backend/internal/adapter/webhook/` that verifies the `PAYLOAD_TYPE_JWT` body via the existing `auth.WebhookValidator.ValidateWebhookToken` (JWKS signature) — reuse the exact pattern from `pre_access_token_handler.go`; do NOT introduce HMAC verification.
- [ ] 2.2 Parse `request.checks.user.userId` from the JWT private claims (round-trip `token.PrivateClaims()` through JSON, as the existing handler does for `user.human.email`).
- [ ] 2.3 Register the handler on a new route on the existing internal-only webhook listener (`server.NewWebhookServer` map in `internal/di/provider.go`), using a second `WebhookValidator` sharing the JWKS cache.

## 3. Backend `sub → UserId` mapping + non-blocking publish

- [ ] 3.1 Inject `UserUseCase` (or a narrow lookup interface) into the handler via DI; regenerate mocks (`mockery`) as needed.
- [ ] 3.2 Resolve the Zitadel `sub` (`request.checks.user.userId`) to the platform `UserId` via `UserUseCase.GetByExternalID`. On lookup miss / transient error OR when `request.checks.user.userId` is absent, log and skip the analytics emission — never fail the request (always return a success response so `CreateSession` is unaffected).
- [ ] 3.3 Inject the `EventPublisher`; on a resolved login publish the new `ACCOUNT.login` subject carrying the resolved `UserId` (and non-PII `login_method` when available). Make the publish best-effort: log and swallow failures so login is unaffected.

## 4. Backend messaging: `ACCOUNT` stream + subject + consumer method

- [ ] 4.1 Add `SubjectAccountLogin = "ACCOUNT.login"` to `backend/internal/entity/event_data.go` and define its CloudEvent data type (`AccountLoginData` carrying `user_id`), mirroring `UserCreatedData`.
- [ ] 4.2 Add the `ACCOUNT` JetStream stream (`Subjects: ["ACCOUNT.*"]`) to `streams.go`, alongside the existing `USER`/`ARTIST`/… streams.
- [ ] 4.3 Implement `AnalyticsConsumer.HandleAccountLogin` mirroring `HandleUserCreated`: parse data, skip on nil client / empty `UserId`, then `Enqueue(ctx, userID, usecase.EventAccountLogin, properties)`; record consumer metrics.
- [ ] 4.4 Subscribe `HandleAccountLogin` to `entity.SubjectAccountLogin` in `internal/di/consumer.go`'s `AddConsumerHandler` registration.

## 5. cloud-provisioning: KEDA trigger for the new consumer

- [ ] 5.1 Add a `nats-jetstream` trigger (stream `ACCOUNT`, consumer `ACCOUNT_login`, durable = subject with dots→underscores) to `k8s/namespaces/backend/base/consumer/scaledobject.yaml`. Keep the base a complete inventory even though prod pins the consumer to `min=max=1` (trigger inert in prod).

## 6. Signup decision (no duplicate event)

- [ ] 6.1 Confirm `account.signup.completed` is NOT published anywhere; document `EventAccountSignupCompleted` as a no-op alias of `user.created` in `analytics_events.go`.
- [ ] 6.2 Update `docs/analytics/event-catalog.md`: `account.login` → emitted (BE, source = Zitadel `CreateSession` Actions v2 Execution, refresh-excluded by construction); `account.signup.completed` → documented as an alias of `user.created`, not separately emitted.

## 7. Tests

- [ ] 7.1 Handler test: a `CreateSession` response payload with `request.checks.user.userId` → exactly one `ACCOUNT.login` publish with the resolved `UserId`.
- [ ] 7.2 Handler test: a JWT with invalid signature → rejected (401), no publish; a payload missing `request.checks.user.userId` → skip + log, success response, no publish; a `GetByExternalID` miss → skip + log, success response, no publish.
- [ ] 7.3 Handler test: a publish failure does not change the handler's HTTP response (login still succeeds).
- [ ] 7.4 Consumer test for `HandleAccountLogin`: forwarded on valid payload; skipped on nil client / empty `UserId`; `Enqueue` error wrapped as `apperr.ErrInternal`.

## 8. Verification

- [ ] 8.1 `make check` (lint + test) passes in `backend/`.
- [ ] 8.2 `make check` passes in `cloud-provisioning/` (lint-ts; k8s render for the scaledobject).
- [ ] 8.3 `openspec validate emit-auth-events-via-webhook --strict` passes.
- [ ] 8.4 Post-rollout verification in **prod** (dev is intentionally stopped): perform a real interactive login and confirm an `account.login` event appears in PostHog Activity attributed to the platform `UserId`, and confirm the `analytics-consumer` forwarded it (consumer metrics / logs). Perform a token refresh and confirm NO `account.login` is emitted. Do NOT author dev-environment verification tasks.
