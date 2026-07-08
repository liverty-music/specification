# Tasks

> **Context:** the first implementation (`response` execution on `CreateSession`) shipped in backend v1.18.0 + specification #684, then broke prod sign-in and was **reverted** (cloud-provisioning #378) on 2026-07-02. The backend messaging plumbing (`ACCOUNT` stream, `SubjectAccountLogin`, `HandleAccountLogin`, its subscription, KEDA trigger) remains **deployed and reusable**; the webhook **handler payload parsing** and the **Zitadel Action** must be redone for the `event`-execution source. Tasks below are marked `[x]` only where the shipped artifact is still valid as-is.
>
> **Update (2026-07-06):** the redesign shipped (backend v1.19.0, spec #688, CP #379) with a `PAYLOAD_TYPE_JWT` Target. Prod verification (8.5) revealed the event execution fired but the target call failed with `Errors.WebKey.NoActive` — an event-execution JWT target needs an active instance web key this instance lacks. Fixed by switching the Target to `PAYLOAD_TYPE_JSON` + HMAC (design.md Decision 2). Task group 9 below tracks the fix; 8.4/8.5 re-open until it verifies.

## 1. Discover the login `event_type` empirically (DONE)

> **Result (2026-07-03, prod Zitadel Events API):** the login event type is **`session.user.checked`**. It fires once per interactive login through the hosted Login UI (`editor = "Zitadel Login V2 Client"`), carries the user at `payload.userID`, does NOT fire on a `refresh_token` grant (that touches only the `oidc_session` aggregate), and does NOT fire for machine `jwt_profile` grants. The rejected alternative `oidc_session.added` also carries `userID` but fires for M2M token grants too. See design.md Decision 1b.

- [x] 1.1 Queried `ListEvents` (`POST /admin/v1/events/_search`) contrasting a fresh interactive login against `refresh_token` renewals: login → `session.added` → `session.user.checked` → `oidc_session.added`; refresh → only `oidc_session.refresh_token.renewed` + `oidc_session.access_token.added` (no `session.*`).
- [x] 1.2 Selected `session.user.checked` — fires once per interactive login, absent on refresh, carries `payload.userID`. Recorded as Decision 1b.
- [x] 1.3 Confirmed the delivered payload carries `payload.userID` (raw event inspected); the `editor` is the Login-UI service user, so the handler reads `payload.userID`, not `editor`.

## 2. Zitadel `event` Execution resources (cloud-provisioning)

- [x] 2.1 Add a `ZitadelExecutionEvent` dynamic resource in `src/zitadel/dynamic/execution.ts` (condition `{ event: { event } }`), mirroring the existing `ZitadelExecutionRequest`. Remove any residual `ZitadelExecutionResponse` resource left from the reverted attempt.
- [x] 2.2 In `src/zitadel/components/actions-v2.ts`, provision the login Target the same way as `pre-access-token-webhook`: `targetType: 'REST_CALL'`, `payloadType: 'PAYLOAD_TYPE_JWT'` (backend verifies via JWKS — no HMAC secret), `interruptOnError: false`. Point its endpoint at the backend login-event webhook path. Ensure the reverted `CreateSession` Target/Execution is not re-created.
- [x] 2.3 Bind a `ZitadelExecutionEvent` on `event.event = "session.user.checked"` (from task 1) to that Target.
- [x] 2.4 Wire the endpoint URL through `src/zitadel/index.ts` / `constants.ts` alongside `PRE_ACCESS_TOKEN_PATH`.

## 3. Backend webhook handler — parse the `event`-execution payload (adapt the deployed handler)

- [x] 3.1 Adapt the deployed login webhook handler in `backend/internal/adapter/webhook/` to parse the `session.user.checked` `event`-execution payload. The webhook JWT claims are `{event_type, aggregateID, userID, event_payload, ...}`: guard on `event_type == "session.user.checked"`, then **base64-decode `event_payload`** and read its `userID` (the login user). Do NOT use the top-level `userID` (that is the Login-UI editor), and do NOT use `request.checks.user.userId` (does not exist for this source). Keep the `auth.WebhookValidator.ValidateWebhookToken` JWKS verification unchanged.
- [x] 3.2 Rename the route/path from the `CreateSession` framing to a login-event path (e.g. `/account-login-event`); update the `server.NewWebhookServer` map in `internal/di/provider.go` and the cloud-provisioning endpoint URL (task 2.4) to match.
- [x] 3.3 Resolve the Zitadel `userID` to the platform `UserId` via `UserUseCase.GetByExternalID`. On lookup miss / transient error OR when `userID` is absent, log and skip the analytics emission. The execution is fire-and-forget, so always return a success response; login is unaffected regardless.
- [x] 3.4 On a resolved login, publish `entity.SubjectAccountLogin` (`ACCOUNT.login`) carrying the resolved `UserId` (and non-PII `login_method` when the payload exposes it). Best-effort: log and swallow publish failures.

## 4. Backend messaging: `ACCOUNT` stream + subject + consumer method (REUSED — deployed in v1.18.0)

- [x] 4.1 `SubjectAccountLogin = "ACCOUNT.login"` and its `AccountLoginData` type exist in `backend/internal/entity/event_data.go`.
- [x] 4.2 The `ACCOUNT` JetStream stream (`Subjects: ["ACCOUNT.*"]`) exists in `streams.go`.
- [x] 4.3 `AnalyticsConsumer.HandleAccountLogin` exists (parse data → skip on nil client / empty `UserId` → `Enqueue(ctx, userID, usecase.EventAccountLogin, properties)`; records consumer metrics).
- [x] 4.4 `HandleAccountLogin` is subscribed to `entity.SubjectAccountLogin` in `internal/di/consumer.go`.
- [x] 4.5 Re-confirm the above four are still present and correct on current `main` after the revert (the revert touched cloud-provisioning, not backend, but verify no backend cleanup removed them).

## 5. cloud-provisioning: KEDA trigger for the consumer

- [x] 5.1 The `nats-jetstream` trigger (stream `ACCOUNT`, consumer `ACCOUNT_login`) is present in `k8s/namespaces/backend/base/consumer/scaledobject.yaml` (inert in prod at `min=max=1`, kept for base completeness).
- [x] 5.2 The revert (`c650111`) removed the ACCOUNT KEDA trigger along with the CreateSession Target/Execution, so it was **re-added** in this change (not merely confirmed). Verified via `kubectl kustomize` render (18 nats-jetstream triggers, incl. `ACCOUNT`/`ACCOUNT_login`).

## 6. Signup decision (no duplicate event — already shipped, confirm intact)

- [x] 6.1 `account.signup.completed` is not published anywhere; `EventAccountSignupCompleted` is documented as a no-op alias of `user.created` in `analytics_events.go`.
- [x] 6.2 `docs/analytics/event-catalog.md` documents `account.signup.completed` as an alias of `user.created`.
- [x] 6.3 Correct the `account.login` catalogue entry in `docs/analytics/event-catalog.md`: source = Zitadel Actions v2 **`event` execution** on the login event type (refresh-excluded), replacing the reverted `CreateSession` Execution description.

## 7. Tests (redo for the `event`-execution payload)

- [x] 7.1 Handler test: an `event`-execution payload with a `userID` → exactly one `ACCOUNT.login` publish with the resolved `UserId`.
- [x] 7.2 Handler test: a JWT with invalid signature → rejected, no publish; a payload missing `userID` → skip + log, success response, no publish; a `GetByExternalID` miss → skip + log, success response, no publish.
- [x] 7.3 Handler test: a publish failure does not change the handler's HTTP response.
- [x] 7.4 Confirm the consumer test for `HandleAccountLogin` still passes unchanged (forwarded on valid payload; skipped on nil client / empty `UserId`; `Enqueue` error wrapped as `apperr.ErrInternal`).
- [x] 7.5 Delete/replace the obsolete `CreateSession`-payload handler tests (they assert `request.checks.user.userId`, which no longer applies).

## 8. Verification & ship to prod

- [x] 8.1 `make check` (lint + test) passes in `backend/`.
- [x] 8.2 `make check` passes in `cloud-provisioning/` (lint-ts; k8s render for the scaledobject).
- [x] 8.3 `openspec validate emit-auth-events-via-webhook --strict` passes.
- [x] 8.4 Merge the backend PR; cut a backend Release (tag `vX.Y.Z`) so the adapted handler ships to prod. Merge the cloud-provisioning PR (Zitadel `event` Execution) → prod Pulumi up creates the Target/Execution.
- [x] 8.5 Post-rollout verification in **prod** (dev is intentionally stopped): perform a real interactive login and confirm exactly one `account.login` appears in PostHog Activity attributed to the platform `UserId`, and that the `analytics-consumer` forwarded it (consumer metrics / logs). Perform a token refresh and confirm NO `account.login` is emitted. **Confirm sign-in still works** (the failure the reverted approach caused). Do NOT author dev-environment verification tasks.

## 9. Fix: `Errors.WebKey.NoActive` → `PAYLOAD_TYPE_JSON` + HMAC (design.md Decision 2)

- [x] 9.1 Backend: rewrite the login-event handler to verify the `ZITADEL-Signature` HMAC header via `actions.ValidateRequestPayload(body, &r.Header, signingKey)` (zitadel-go SDK) instead of JWKS; parse the raw JSON body (no JWT), keep the `event_type` guard + base64 `event_payload` decode. Config: replace `WEBHOOK_LOGIN_EVENT_AUDIENCE` with `WEBHOOK_LOGIN_EVENT_SIGNING_KEY` (secret, optional so a boot before the key syncs degrades gracefully — handler returns 401). Rewrite handler tests to sign with `actions.ComputeSignatureHeader`.
- [x] 9.2 cloud-provisioning (Pulumi): set the login-event Target `payloadType: 'PAYLOAD_TYPE_JSON'`; capture Zitadel's generated `signingKey` from the Target and store it as GSM secret `webhook-login-event-signing-key` (threaded via `Gcp` → KubernetesComponent secrets list, backend-app + ESO IAM), following the `posthog-public-project-key` pattern.
- [x] 9.3 Ship backend (release `v1.19.1`) → prod; run cloud-provisioning prod `pulumi up` (re-creates the Target as JSON, generates the signingKey, writes the GSM secret). MANUAL Pulumi Cloud console.
- [x] 9.4 Follow-up (only AFTER 9.3's prod `pulumi up` created the GSM secret): add the `WEBHOOK_LOGIN_EVENT_SIGNING_KEY` → `webhook-login-event-signing-key` entry to `k8s/namespaces/backend/base/server/external-secret.yaml`. Deferred because ESO v1beta1 fails the whole `backend-secrets` bundle when a referenced remote key is absent (same two-phase pattern as `posthog-public-project-key`). ArgoCD sync → ESO mounts the key → backend restart picks it up.
- [x] 9.5 Re-verify 8.5 in prod: interactive login → `account.login` in PostHog attributed to the platform `UserId`; refresh → none; sign-in still works; confirm the Zitadel log no longer shows `WebKey.NoActive` for the login-event target.
