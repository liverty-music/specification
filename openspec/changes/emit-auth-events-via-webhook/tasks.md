# Tasks

## 1. Payload spike + gating design decision (do this FIRST)

- [ ] 1.1 On a dev Zitadel instance, temporarily dump the full decoded `pre_access_token` private-claims payload from the existing handler.
- [ ] 1.2 Exercise BOTH flows and capture both payloads: (a) a fresh interactive login, (b) a silent `refresh_token` grant. Diff them for any field that reliably differs (`amr`, a fresh `auth_time` ≈ now, or an explicit refresh-grant indicator).
- [ ] 1.3 Record the spike outcome as the build-time decision (Decision 0):
  - **Outcome A** — a reliable discriminator IS present → the `pre_access_token` webhook MAY be used (path in task group 3-alt).
  - **Outcome B** (expected, given the resource-context payload shape) — NO reliable discriminator → the `pre_access_token` webhook CANNOT carry login semantics; use the session-created Action (default path, task group 3).
- [ ] 1.4 Remove the temporary payload dump from the handler before shipping. There is NO runtime "suppress when uncertain" code path — undiscriminability was resolved here, once, not per request.

## 2. `sub → UserId` mapping on the login path (source-agnostic)

- [ ] 2.1 On a user-initiated login only, resolve the Zitadel `sub` to the platform `UserId` via the existing `UserUseCase.GetByExternalID`.
- [ ] 2.2 Handle lookup miss / transient error by logging and skipping the analytics emission — never fail the login / token-issuance flow.
- [ ] 2.3 Wire the `UserUseCase` (or a narrow lookup interface) into the login handler via DI; regenerate mocks (`mockery`) as needed.

## 3. PRIMARY path — session-created Action login handler (default, use unless spike Outcome A)

- [ ] 3.1 Register a Zitadel session-created Actions v2 Target and its webhook-specific audience; this hook fires on user-initiated login and structurally cannot fire on a `refresh_token` grant.
- [ ] 3.2 Add a session-created handler in `backend/internal/adapter/webhook/` that validates the JWT against the new audience and parses `sub` from the payload; wire it into the server routing and DI.
- [ ] 3.3 Inject the `EventPublisher`; on a login, publish the new `ACCOUNT.login` subject carrying the resolved `UserId` (and non-PII `login_method` when available). Make the publish best-effort: log and swallow failures so login is unaffected.
- [ ] 3.4 Unit-test: a session-created payload → exactly one `ACCOUNT.login` publish; a publish failure does not change the handler's HTTP response (login still succeeds).

## 3-alt. CONDITIONAL path — extend `pre_access_token` discrimination (ONLY if spike Outcome A)

- [ ] 3a.1 Extend the `pre_access_token` payload model to parse the discriminator field the spike proved present; implement the fresh-auth predicate from that field (no guessing — the field is known to exist).
- [ ] 3a.2 On fresh auth only, publish `ACCOUNT.login` (resolved `UserId`, non-PII `login_method`) best-effort as in 3.3; on refresh, publish nothing.
- [ ] 3a.3 Unit-test: fresh-auth payload → exactly one publish; refresh payload → zero publishes; publish failure does not affect token issuance.

## 4. NATS subject + analytics-consumer Handle method

- [ ] 4.1 Add `SubjectAccountLogin = "ACCOUNT.login"` to `backend/internal/entity/event_data.go` and define its CloudEvent data type (carrying `user_id`).
- [ ] 4.2 Provision the new `ACCOUNT` JetStream stream alongside the existing `USER`/`ARTIST`/… streams.
- [ ] 4.3 Implement `AnalyticsConsumer.HandleAccountLogin` mirroring `HandleUserCreated`: parse data, skip on nil client / empty `UserId`, then `Enqueue(ctx, userID, usecase.EventAccountLogin, properties)`; record consumer metrics.
- [ ] 4.4 Subscribe `HandleAccountLogin` to `ACCOUNT.login` in the consumer's registration.

## 5. Signup decision (no duplicate event)

- [ ] 5.1 Confirm `account.signup.completed` is NOT published anywhere; document `EventAccountSignupCompleted` as a no-op alias of `user.created` in `analytics_events.go`.
- [ ] 5.2 Update `docs/analytics/event-catalog.md`: `account.login` → emitted (BE, source = Zitadel webhook, refresh-excluded); `account.signup.completed` → documented as an alias of `user.created`, not separately emitted.

## 6. Tests

- [ ] 6.1 Consumer test for `HandleAccountLogin`: forwarded on valid payload; skipped on nil client / empty `UserId`; `Enqueue` error wrapped as `apperr.ErrInternal`.
- [ ] 6.2 End-to-end-style handler test for the chosen source: a user-initiated login → exactly one `ACCOUNT.login` publish with the resolved `UserId`. Under the primary session-created path, also assert no second login handler exists on the refresh path; under the conditional `pre_access_token` path, assert a refresh payload → zero publishes.

## 7. Verification

- [ ] 7.1 `make check` (lint + test) passes in `backend/`.
- [ ] 7.2 `openspec validate emit-auth-events-via-webhook --strict` passes.
