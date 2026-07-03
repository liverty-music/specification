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

### Decision 1: Emit `account.login` from a Zitadel Actions v2 `event` Execution

The login signal is a Zitadel Actions v2 **`event` Execution** on `event.event = "session.user.checked"` (see Decision 1b for why this exact type), invoking a webhook **Target** that points at the backend handler. An `event` execution fires **after** the login event is persisted to the Zitadel eventstore, receives the stored event payload, and **cannot manipulate any API request or response**. This is Zitadel's documented pattern for reacting to events / running side-effects ([Actions v2 concepts](https://zitadel.com/docs/concepts/features/actions_v2), [Actions v2 usage](https://zitadel.com/docs/guides/integrate/actions/usage)).

**Why an `event` execution and not a method (`request`/`response`) execution — the load-bearing lesson from the 2026-07-02 outage.** The reverted attempt used a `response` execution on `/zitadel.session.v2.SessionService/CreateSession`. A method execution does **not** observe the call: its webhook return **replaces** the API request (`request` condition) or response (`response` condition) body — there is **no observe-only mode**, and `interruptOnError:false` only suppresses error-based blocking, not the replacement (a successful 200 still replaces the payload). The handler returned `{}`, which stripped `sessionId` from the `CreateSession` response; the Login UI v2 then called `GetSession("")` and **new interactive sign-ins failed instance-wide**. An `event` execution has no such power — it is delivered after the fact and its return is ignored — so it is immune to this failure mode by construction. This is the primary reason the source is an `event` execution.

**Why `CreateSession` was also the wrong source regardless.** In the hosted Login UI v2 flow the session is created first and the user is attached by a later `SetSession`, so `CreateSession` carries no login user (`request.checks.user.userId` was absent on every call). An `event` execution instead binds to the *user* aggregate's login event, whose `userID` is the logging-in user directly.

**Login-specificity.** The chosen event type (Decision 1b) fires once per user-initiated login and not on a silent `refresh_token` grant (which reuses the existing session and mints a token without a fresh login event). There is nothing to discriminate at runtime: login-specificity is a property of the event type, fixed once by empirical discovery, not a per-request heuristic. Our Zitadel is v4.7.1+, so Actions v2 Executions are GA.

### Decision 1b: The login `event_type` is `session.user.checked` (determined empirically via the Events API)

The event type was **not guessed** — it was discovered by querying the prod Zitadel Events API (`ListEvents`, `POST /admin/v1/events/_search`, 2026-07-03) and contrasting the events a fresh interactive login produces against those a `refresh_token` renewal produces. Findings:

- **`session.user.checked`** (chosen). Fires once per interactive login, on the `session` aggregate, with `editor = "Zitadel Login V2 Client"` — i.e. only through the hosted Login UI v2 flow. Its `payload.userID` carries the logging-in user. It does **not** fire on refresh (a refresh touches the `oidc_session` aggregate, never the `session`), and it does **not** fire for machine (jwt_profile / M2M) token grants, which never create a Login-UI session. This makes it login-specific *and* human-specific with no runtime filtering.
- **`oidc_session.added`** (rejected alternative). Also carries `payload.userID` and is refresh-excluded, but it fires for **every** OIDC session establishment — including machine `jwt_profile` grants (observed: the probe's own `pulumi-admin` token mints each produced an `oidc_session.added`). Binding here would fire the webhook on all M2M token traffic; the `userID → UserId` lookup would then drop each (a machine user is not a platform user), but only after needless webhook + NATS load. `session.user.checked` avoids that traffic entirely.
- **`oidc_session.access_token.added`** (rejected). Fires on both login *and* refresh — not login-specific.

Login-specificity is therefore a property of the chosen event type (verified against real data), not a per-request runtime heuristic. This replaces the old gating "payload spike", which only existed to evaluate the discarded `pre_access_token` hook.

> **Residual edge (bounded, accepted):** `session.user.checked` reflects an *interactive authentication*. A returning user whose Login-UI session cookie is still valid may re-enter the app without re-authenticating (no new `session.user.checked`); that "opened the app with a live session" case is a separate frontend concern, not a server-side login. Conversely an MFA step-up mid-session could in principle re-check the user; in the sampled logins `session.user.checked` appeared exactly once per session, so this is not observed in practice.

### Decision 2: Verify the Target the same way as `pre_access_token` — `PAYLOAD_TYPE_JWT` + JWKS, not HMAC

The login `event`-execution Target is provisioned with `payloadType: 'PAYLOAD_TYPE_JWT'` and `interruptOnError: false` (analytics must never block login). The backend handler reuses `auth.WebhookValidator.ValidateWebhookToken`, which verifies the JWT **signature against the shared Zitadel JWKS cache** — the exact security boundary the deployed `pre_access_token` handler uses. It then round-trips `token.PrivateClaims()` through JSON and unmarshals the subset it needs (the event payload's `userID`).

Zitadel's HMAC signing (`ZITADEL-Signature` header + `signingKey`) applies only to `PAYLOAD_TYPE_JSON`/`PAYLOAD_TYPE_JWE` Targets, which this project deliberately does not use. Introducing an HMAC secret would be a *new* pattern; reusing JWKS is the established one and needs no new secret material. Replay is mitigated as for the existing handler: the webhook listener is a private, internal-only port (unreachable via the public Gateway), and the handler's payload-shape expectations reject a JWT minted for a different Target.

### Decision 3: `userID → UserId` lookup on the login path

`Enqueue` needs the platform `UserId`; the login user is carried in the event's own payload. The Actions v2 **event-execution** webhook delivers a JWT whose claims are `{ aggregateID, aggregateType, resourceOwner, instanceID, sequence, event_type, created_at, userID, event_payload }`. Two gotchas fixed by the empirical inspection:

1. The **top-level `userID` is the event editor** — for `session.user.checked` that is the Login-UI service user (`"Zitadel Login V2 Client"`), NOT the person logging in. The handler MUST NOT use it.
2. The **`event_payload` is base64-encoded**. The handler base64-decodes it, JSON-unmarshals `{ userID }`, and that `userID` (the `session.user.checked` payload's own field) is the logging-in user.

The handler then resolves that `userID → UserId` via the existing `UserUseCase.GetByExternalID` (already defined in `user_uc.go`, "retrieves a user by identity provider ID (Zitadel sub claim)"). It SHOULD also guard on `event_type == "session.user.checked"` and skip anything else. The event fires only on a user-initiated login, never on refresh, so refreshes incur no extra query; and because a machine `jwt_profile` grant never produces `session.user.checked`, no M2M traffic reaches this handler at all. The resolved `UserId` becomes the NATS event payload's `user_id` and ultimately the PostHog `distinct_id`. If the lookup fails (user not yet provisioned, or transient error) or `payload.userID` is absent, the handler logs and skips the analytics emission — and because the execution is fire-and-forget, the handler's response never affects login regardless.

### Decision 4: Analytics wiring is publish-to-NATS, non-blocking, via a new `ACCOUNT.login` subject and `HandleAccountLogin`

The login handler does **not** call PostHog (consistent with "webhook handlers MUST NOT call the PostHog SDK directly"). On a login it publishes a new subject `ACCOUNT.login` (new `ACCOUNT` stream, following the UPPERCASE two-segment convention in `entity/event_data.go`) carrying the resolved `UserId`. `streams.go` gains an `ACCOUNT` stream (`Subjects: ["ACCOUNT.*"]`; single-token subject, so `*` suffices — unlike the nested `SALES_PHASE.>`). The `analytics-consumer` gains `HandleAccountLogin`, which mirrors `HandleUserCreated`: parse the CloudEvent data, skip on nil client / empty `UserId`, then `client.Enqueue(ctx, userID, usecase.EventAccountLogin, properties)`; record consumer metrics. The publish is fire-and-forget on the login path: a publish failure is logged and swallowed so login latency and success are unaffected. This keeps the login-specificity concern (the source Action, Decision 1) and the delivery concern (forwarding at the consumer) in two clean layers, matching the rest of the analytics backend.

The properties payload stays minimal and non-PII (e.g. `login_method` from the Action payload when available); no email or `sub` is ever placed in properties.

The consumer subject also needs its scaling trigger: a KEDA `nats-jetstream` trigger (stream `ACCOUNT`, consumer `ACCOUNT_login` — the durable is the subject with dots replaced by underscores, per the subscriber's `DurableCalculator`) is added to the cloud-provisioning consumer `scaledobject.yaml` base. Prod pins the consumer to `min=max=1`, which makes the trigger inert in prod, but the base MUST stay a complete inventory, so it is added anyway.

### Decision 5: `account.signup.completed` is an alias of `user.created`; no new event is emitted

Per Decision 15's still-valid first half, signup and `user.created` are the same instant. This change emits **no** `account.signup.completed`. `user.created` remains the canonical signup signal (already published by `user_uc.go` and forwarded by `AnalyticsConsumer.HandleUserCreated`). The `EventAccountSignupCompleted` constant is retained only as a documented alias/no-op so dashboards referring to "signup" resolve to `user.created`; no publisher is wired for it. This avoids double-counting signups in any summed funnel.

## Risks / Trade-offs

- **[Risk] The chosen `event_type` mis-fires (over- or under-counts logins).** If the wrong event is bound — one that also fires on refresh/token-mint, or one that does not fire on every user-initiated login — the login metric is wrong. **Mitigation:** Decision 1b fixes the type empirically from `ListEvents` output that explicitly contrasts a fresh login against a refresh, and task group 7 asserts the refresh case emits nothing; the recorded query is the auditable justification. Because the type is fixed at build time from observed events (not guessed), this is verified once rather than hoped for at runtime.

- **[Risk / eliminated] The reverted `response` execution broke sign-in by replacing the API response.** A method (`request`/`response`) execution's webhook return replaces the API payload; returning `{}` stripped `sessionId` and failed all new logins on 2026-07-02. **Mitigation:** eliminated by construction — an `event` execution is delivered after the event is stored and its return is ignored, so it cannot alter `CreateSession`/`SetSession` or any other API response. No method execution is used for this signal.

- **[Risk] Login-event delivery reliability bounds login-count completeness.** The analytics publish is intentionally best-effort and non-blocking, so a NATS publish failure silently drops that one login event. **Mitigation:** accept eventual under-count for analytics (never block login); the consumer's existing retry/backoff handles PostHog-side transients once the NATS message exists; `analytics_consumer_*` metrics surface drops. This is a *delivery* gap (a genuinely-login event that failed to publish), categorically different from the over-count the old `pre_access_token` approach would have caused.

- **[Trade-off] The login `event` execution adds net-new Zitadel surface** (a Target, an `event`-condition Execution requiring a new `ZitadelExecutionEvent` dynamic resource) versus reusing the already-deployed `pre_access_token` Target. We accept this cost deliberately: the login event is login-specific and, being an `event` execution, cannot affect the auth flow — whereas reusing the token-issuance hook would re-introduce the refresh over-count Decision 15 deferred the event to avoid. The backend messaging plumbing (stream, subject, consumer, KEDA trigger) is *not* net-new — it was deployed in v1.18.0 and is reused; only the handler's payload parsing changes.

- **[Trade-off] No `account.signup.completed` event** means any external consumer expecting that literal name must map to `user.created`. Accepted: a single canonical signup signal is strictly better than two names for one instant, and the catalogue documents the alias.
