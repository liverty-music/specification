## Context

`introduce-analytics-tool` (archived) built the backend analytics path: Connect-RPC handlers / use cases publish UPPERCASE two-segment NATS subjects (`USER.created`, `ARTIST.followed`, …); an `analytics-consumer` (`backend/internal/adapter/event/analytics_consumer.go`) subscribes, and each `Handle*` method maps its subject to a lowercase catalogue event and calls `AnalyticsClient.Enqueue(ctx, userID, eventName, properties)`. `Enqueue` requires the platform `UserId` (UUID) as `distinct_id` and rejects an empty/non-UUID value — the Zitadel `sub` claim is explicitly NOT a valid `distinct_id`.

That change's Decision 15 descoped the two `account.*` auth events:

- `account.signup.completed` fired at the same instant as `user.created` (`user_uc.go` already publishes `SubjectUserCreated` on user creation, and the consumer already forwards it as `user.created`). A second event would double-count signups.
- `account.login` had no clean signal. The existing `pre_access_token` webhook handler (`backend/internal/adapter/webhook/pre_access_token_handler.go`) fires on **every access-token mint, including silent refresh-token grants**, so emitting `account.login` there over-counts logins.

The product owner has reversed the *deferral* of `account.login` (it is the primary returning-active-user signal for retention cohorts). The reasoning that a refresh is not a login, and that signup must not be double-counted, still holds. This change must satisfy the owner's request without regressing analytics correctness.

The Zitadel webhook already in production is an Actions v2 **Target** invoked with a `PAYLOAD_TYPE_JWT` body: the request body is a JWT whose private claims carry the Actions v2 function payload. The existing handler verifies that JWT's **signature against the Zitadel instance JWKS** (`auth.WebhookValidator.ValidateWebhookToken`) and reads nested fields from the private claims (e.g. `user.human.email`). No shared HMAC secret is used — the cloud-provisioning Target is `PAYLOAD_TYPE_JWT` precisely so the backend can reuse its JWKS validator. This change reuses that exact verification pattern for the new login Target.

## Goals / Non-Goals

**Goals**

- Emit `account.login` exactly once per **user-initiated login**, attributed to the platform `UserId`.
- Guarantee a token **refresh** does NOT emit `account.login`.
- Keep the analytics path non-fatal and non-blocking on the login / session-creation critical path.
- Resolve `account.signup.completed` without emitting a duplicate of `user.created`.
- Reuse the established publisher → NATS subject → `analytics-consumer` `Handle*` → PostHog pattern; do not call PostHog from the webhook handler directly.

**Non-Goals**

- No new Connect-RPC, no proto change, no DB schema change.
- No frontend emission of `account.login` (BE-sourced / trust-critical per the catalogue).
- No backfill of historical logins; instrumentation is forward-only.
- No reopening of the broader analytics taxonomy beyond these two account events.

## Decisions

### Decision 1: Emit `account.login` from a Zitadel `CreateSession` Actions v2 Execution (official best practice)

The login signal is a Zitadel Actions v2 **Execution** whose condition targets the API method `/zitadel.session.v2.SessionService/CreateSession`, invoking a webhook **Target** that points at a new backend handler. This is Zitadel's documented pattern for reacting to logins ([Advanced Session Management with Actions V2](https://zitadel.com/blog/session-management-actions-v2); [Actions v2 concepts](https://zitadel.com/docs/concepts/features/actions_v2)).

**Why this is login-specific by construction.** `CreateSession` establishes a **new interactive session** (its initial checks / challenges). The OIDC `refresh_token` grant mints a new access token "without user interaction" ([OIDC endpoints](https://zitadel.com/docs/apis/openidoauth/endpoints)) and reuses the existing session — it does **not** call `CreateSession`. So subscribing to `CreateSession` fires once per user-initiated login and **structurally never on refresh**. There is nothing to discriminate: no payload spike, no `amr`/`auth_time` inspection, no per-request "suppress when uncertain" heuristic. The earlier design's gating payload spike (on a now-stopped dev Zitadel) is removed entirely — it only existed to evaluate reusing the inferior `pre_access_token` hook, which this decision discards.

Our Zitadel is v4.7.1+, so Actions v2 Executions are GA (the blog's "GA with V4" note is satisfied).

### Decision 1a: Use the `response` condition, not `request`

The blog example uses a `request` condition (it manipulates the in-flight session). For analytics the question is "**did a login succeed?**", so the `response` side is correct: a `response` Execution fires **after** Zitadel has produced a successful `CreateSession` response, so a `CreateSession` that errors out does not emit a spurious login.

This is viable because a `response`-condition payload carries **both** the `request` and the `response` objects (Zitadel's payload shape for a method Execution is `{ fullMethod, instanceID, orgID, userID, request, response }`). The login user identifier is therefore still reachable at `request.checks.user.userId` on the response side. The top-level `userID` is the *acting* caller of the API (often the login app / empty for the hosted login flow), so `request.checks.user.userId` — the user the session is being created **for** — is the correct field.

**Rationale (one line):** response side = record only logins that actually succeeded, with no extra work to exclude failed `CreateSession` attempts.

### Decision 2: Verify the Target the same way as `pre_access_token` — `PAYLOAD_TYPE_JWT` + JWKS, not HMAC

The new `CreateSession` Target is provisioned with `payloadType: 'PAYLOAD_TYPE_JWT'` and `interruptOnError: false` (analytics must never block login). The backend handler reuses `auth.WebhookValidator.ValidateWebhookToken`, which verifies the JWT **signature against the shared Zitadel JWKS cache** — the exact security boundary the deployed `pre_access_token` handler uses. It then round-trips `token.PrivateClaims()` through JSON and unmarshals the subset it needs (`request.checks.user.userId`).

Zitadel's HMAC signing (`ZITADEL-Signature` header + `signingKey`) applies only to `PAYLOAD_TYPE_JSON`/`PAYLOAD_TYPE_JWE` Targets, which this project deliberately does not use. Introducing an HMAC secret would be a *new* pattern; reusing JWKS is the established one and needs no new secret material. Replay is mitigated as for the existing handler: the webhook listener is a private, internal-only port (unreachable via the public Gateway), and the handler's payload-shape expectations reject a JWT minted for a different Target.

### Decision 3: `sub → UserId` lookup on the login path

`Enqueue` needs the platform `UserId`; the Action payload carries the Zitadel `sub` at `request.checks.user.userId`. The handler resolves `sub → UserId` via the existing `UserUseCase.GetByExternalID` (already defined in `user_uc.go`, "retrieves a user by identity provider ID (Zitadel sub claim)"). The lookup runs only on `CreateSession` — i.e. only on a user-initiated login, never on refresh — so refreshes incur no extra query. The resolved `UserId` becomes the NATS event payload's `user_id` and ultimately the PostHog `distinct_id`. If the lookup fails (user not yet provisioned, or transient error) or `request.checks.user.userId` is absent, the handler logs and skips the analytics emission — it never fails the session-creation / login flow.

### Decision 4: Analytics wiring is publish-to-NATS, non-blocking, via a new `ACCOUNT.login` subject and `HandleAccountLogin`

The login handler does **not** call PostHog (consistent with "webhook handlers MUST NOT call the PostHog SDK directly"). On a login it publishes a new subject `ACCOUNT.login` (new `ACCOUNT` stream, following the UPPERCASE two-segment convention in `entity/event_data.go`) carrying the resolved `UserId`. `streams.go` gains an `ACCOUNT` stream (`Subjects: ["ACCOUNT.*"]`; single-token subject, so `*` suffices — unlike the nested `SALES_PHASE.>`). The `analytics-consumer` gains `HandleAccountLogin`, which mirrors `HandleUserCreated`: parse the CloudEvent data, skip on nil client / empty `UserId`, then `client.Enqueue(ctx, userID, usecase.EventAccountLogin, properties)`; record consumer metrics. The publish is fire-and-forget on the login path: a publish failure is logged and swallowed so login latency and success are unaffected. This keeps the login-specificity concern (the source Action, Decision 1) and the delivery concern (forwarding at the consumer) in two clean layers, matching the rest of the analytics backend.

The properties payload stays minimal and non-PII (e.g. `login_method` from the Action payload when available); no email or `sub` is ever placed in properties.

The consumer subject also needs its scaling trigger: a KEDA `nats-jetstream` trigger (stream `ACCOUNT`, consumer `ACCOUNT_login` — the durable is the subject with dots replaced by underscores, per the subscriber's `DurableCalculator`) is added to the cloud-provisioning consumer `scaledobject.yaml` base. Prod pins the consumer to `min=max=1`, which makes the trigger inert in prod, but the base MUST stay a complete inventory, so it is added anyway.

### Decision 5: `account.signup.completed` is an alias of `user.created`; no new event is emitted

Per Decision 15's still-valid first half, signup and `user.created` are the same instant. This change emits **no** `account.signup.completed`. `user.created` remains the canonical signup signal (already published by `user_uc.go` and forwarded by `AnalyticsConsumer.HandleUserCreated`). The `EventAccountSignupCompleted` constant is retained only as a documented alias/no-op so dashboards referring to "signup" resolve to `user.created`; no publisher is wired for it. This avoids double-counting signups in any summed funnel.

## Risks / Trade-offs

- **[Risk] `request.checks.user.userId` may be absent for some login flows.** `CreateSession`'s `checks.user` is a oneof (`userId` **or** `loginName`), and a hosted-login flow may create the session first and attach the user via a later `SetSession`, so the `CreateSession` response payload can lack `checks.user.userId`. **Mitigation:** the handler treats a missing/empty identifier exactly like a failed `sub → UserId` lookup — log and skip, never fail login. This bounds login-count completeness (an acceptable under-count) rather than emitting a wrong `distinct_id`. If under-count proves material in PostHog after rollout, the fallback is a second Execution on `SetSession` (or a `GetSession` lookup from the `response.sessionId`); that is deliberately out of scope until the data shows it is needed.

- **[Risk] Login-event delivery reliability bounds login-count completeness.** The analytics publish is intentionally best-effort and non-blocking, so a NATS publish failure silently drops that one login event. **Mitigation:** accept eventual under-count for analytics (never block login); the consumer's existing retry/backoff handles PostHog-side transients once the NATS message exists; `analytics_consumer_*` metrics surface drops. This is a *delivery* gap (a genuinely-login event that failed to publish), categorically different from the over-count the old `pre_access_token` approach would have caused.

- **[Trade-off] The `CreateSession` Action adds net-new Zitadel/infra surface** (a new Target, a `response`-condition Execution requiring a new `ZitadelExecutionResponse` dynamic resource, a second webhook handler) versus reusing the already-deployed `pre_access_token` Target. We accept this cost deliberately: the `CreateSession` hook is login-specific by construction, so it meets the goal without depending on the shape of the `pre_access_token` payload. Reusing the token-issuance hook would have re-introduced exactly the refresh over-count Decision 15 deferred the event to avoid.

- **[Trade-off] No `account.signup.completed` event** means any external consumer expecting that literal name must map to `user.created`. Accepted: a single canonical signup signal is strictly better than two names for one instant, and the catalogue documents the alias.
