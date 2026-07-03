# Tasks

> **Context:** the first implementation (`response` execution on `CreateSession`) shipped in backend v1.18.0 + specification #684, then broke prod sign-in and was **reverted** (cloud-provisioning #378) on 2026-07-02. The backend messaging plumbing (`ACCOUNT` stream, `SubjectAccountLogin`, `HandleAccountLogin`, its subscription, KEDA trigger) remains **deployed and reusable**; the webhook **handler payload parsing** and the **Zitadel Action** must be redone for the `event`-execution source. Tasks below are marked `[x]` only where the shipped artifact is still valid as-is.

## 1. Discover the login `event_type` empirically (DONE)

> **Result (2026-07-03, prod Zitadel Events API):** the login event type is **`session.user.checked`**. It fires once per interactive login through the hosted Login UI (`editor = "Zitadel Login V2 Client"`), carries the user at `payload.userID`, does NOT fire on a `refresh_token` grant (that touches only the `oidc_session` aggregate), and does NOT fire for machine `jwt_profile` grants. The rejected alternative `oidc_session.added` also carries `userID` but fires for M2M token grants too. See design.md Decision 1b.

- [x] 1.1 Queried `ListEvents` (`POST /admin/v1/events/_search`) contrasting a fresh interactive login against `refresh_token` renewals: login → `session.added` → `session.user.checked` → `oidc_session.added`; refresh → only `oidc_session.refresh_token.renewed` + `oidc_session.access_token.added` (no `session.*`).
- [x] 1.2 Selected `session.user.checked` — fires once per interactive login, absent on refresh, carries `payload.userID`. Recorded as Decision 1b.
- [x] 1.3 Confirmed the delivered payload carries `payload.userID` (raw event inspected); the `editor` is the Login-UI service user, so the handler reads `payload.userID`, not `editor`.

## 2. Zitadel `event` Execution resources (cloud-provisioning)

- [ ] 2.1 Add a `ZitadelExecutionEvent` dynamic resource in `src/zitadel/dynamic/execution.ts` (condition `{ event: { event } }`), mirroring the existing `ZitadelExecutionRequest`. Remove any residual `ZitadelExecutionResponse` resource left from the reverted attempt.
- [ ] 2.2 In `src/zitadel/components/actions-v2.ts`, provision the login Target the same way as `pre-access-token-webhook`: `targetType: 'REST_CALL'`, `payloadType: 'PAYLOAD_TYPE_JWT'` (backend verifies via JWKS — no HMAC secret), `interruptOnError: false`. Point its endpoint at the backend login-event webhook path. Ensure the reverted `CreateSession` Target/Execution is not re-created.
- [ ] 2.3 Bind a `ZitadelExecutionEvent` on `event.event = "session.user.checked"` (from task 1) to that Target.
- [ ] 2.4 Wire the endpoint URL through `src/zitadel/index.ts` / `constants.ts` alongside `PRE_ACCESS_TOKEN_PATH`.

## 3. Backend webhook handler — parse the `event`-execution payload (adapt the deployed handler)

- [ ] 3.1 Adapt the deployed login webhook handler in `backend/internal/adapter/webhook/` to parse the `session.user.checked` `event`-execution payload: read the Zitadel user from `payload.userID` (NOT `request.checks.user.userId`, which does not exist for this source; NOT `editor`, which is the Login-UI service user). Keep the `auth.WebhookValidator.ValidateWebhookToken` JWKS verification unchanged.
- [ ] 3.2 Rename the route/path from the `CreateSession` framing to a login-event path (e.g. `/account-login-event`); update the `server.NewWebhookServer` map in `internal/di/provider.go` and the cloud-provisioning endpoint URL (task 2.4) to match.
- [ ] 3.3 Resolve the Zitadel `userID` to the platform `UserId` via `UserUseCase.GetByExternalID`. On lookup miss / transient error OR when `userID` is absent, log and skip the analytics emission. The execution is fire-and-forget, so always return a success response; login is unaffected regardless.
- [ ] 3.4 On a resolved login, publish `entity.SubjectAccountLogin` (`ACCOUNT.login`) carrying the resolved `UserId` (and non-PII `login_method` when the payload exposes it). Best-effort: log and swallow publish failures.

## 4. Backend messaging: `ACCOUNT` stream + subject + consumer method (REUSED — deployed in v1.18.0)

- [x] 4.1 `SubjectAccountLogin = "ACCOUNT.login"` and its `AccountLoginData` type exist in `backend/internal/entity/event_data.go`.
- [x] 4.2 The `ACCOUNT` JetStream stream (`Subjects: ["ACCOUNT.*"]`) exists in `streams.go`.
- [x] 4.3 `AnalyticsConsumer.HandleAccountLogin` exists (parse data → skip on nil client / empty `UserId` → `Enqueue(ctx, userID, usecase.EventAccountLogin, properties)`; records consumer metrics).
- [x] 4.4 `HandleAccountLogin` is subscribed to `entity.SubjectAccountLogin` in `internal/di/consumer.go`.
- [ ] 4.5 Re-confirm the above four are still present and correct on current `main` after the revert (the revert touched cloud-provisioning, not backend, but verify no backend cleanup removed them).

## 5. cloud-provisioning: KEDA trigger for the consumer (REUSED — deployed in v1.18.0)

- [x] 5.1 The `nats-jetstream` trigger (stream `ACCOUNT`, consumer `ACCOUNT_login`) exists in `k8s/namespaces/backend/base/consumer/scaledobject.yaml` (inert in prod at `min=max=1`, kept for base completeness).
- [ ] 5.2 Confirm the trigger survived the cloud-provisioning revert (#378 reverted the Zitadel Target/Execution, not the KEDA trigger) — re-add if the revert removed it.

## 6. Signup decision (no duplicate event — already shipped, confirm intact)

- [x] 6.1 `account.signup.completed` is not published anywhere; `EventAccountSignupCompleted` is documented as a no-op alias of `user.created` in `analytics_events.go`.
- [x] 6.2 `docs/analytics/event-catalog.md` documents `account.signup.completed` as an alias of `user.created`.
- [ ] 6.3 Correct the `account.login` catalogue entry in `docs/analytics/event-catalog.md`: source = Zitadel Actions v2 **`event` execution** on the login event type (refresh-excluded), replacing the reverted `CreateSession` Execution description.

## 7. Tests (redo for the `event`-execution payload)

- [ ] 7.1 Handler test: an `event`-execution payload with a `userID` → exactly one `ACCOUNT.login` publish with the resolved `UserId`.
- [ ] 7.2 Handler test: a JWT with invalid signature → rejected, no publish; a payload missing `userID` → skip + log, success response, no publish; a `GetByExternalID` miss → skip + log, success response, no publish.
- [ ] 7.3 Handler test: a publish failure does not change the handler's HTTP response.
- [ ] 7.4 Confirm the consumer test for `HandleAccountLogin` still passes unchanged (forwarded on valid payload; skipped on nil client / empty `UserId`; `Enqueue` error wrapped as `apperr.ErrInternal`).
- [ ] 7.5 Delete/replace the obsolete `CreateSession`-payload handler tests (they assert `request.checks.user.userId`, which no longer applies).

## 8. Verification & ship to prod

- [ ] 8.1 `make check` (lint + test) passes in `backend/`.
- [ ] 8.2 `make check` passes in `cloud-provisioning/` (lint-ts; k8s render for the scaledobject).
- [ ] 8.3 `openspec validate emit-auth-events-via-webhook --strict` passes.
- [ ] 8.4 Merge the backend PR; cut a backend Release (tag `vX.Y.Z`) so the adapted handler ships to prod. Merge the cloud-provisioning PR (Zitadel `event` Execution) → prod Pulumi up creates the Target/Execution.
- [ ] 8.5 Post-rollout verification in **prod** (dev is intentionally stopped): perform a real interactive login and confirm exactly one `account.login` appears in PostHog Activity attributed to the platform `UserId`, and that the `analytics-consumer` forwarded it (consumer metrics / logs). Perform a token refresh and confirm NO `account.login` is emitted. **Confirm sign-in still works** (the failure the reverted approach caused). Do NOT author dev-environment verification tasks.
