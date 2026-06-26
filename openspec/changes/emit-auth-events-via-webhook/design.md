## Context

`introduce-analytics-tool` (archived) built the backend analytics path: Connect-RPC handlers / use cases publish UPPERCASE two-segment NATS subjects (`USER.created`, `ARTIST.followed`, …); an `analytics-consumer` (`backend/internal/adapter/event/analytics_consumer.go`) subscribes, and each `Handle*` method maps its subject to a lowercase catalogue event and calls `AnalyticsClient.Enqueue(ctx, userID, eventName, properties)`. `Enqueue` requires the platform `UserId` (UUID) as `distinct_id` and rejects an empty/non-UUID value — the Zitadel `sub` claim is explicitly NOT a valid `distinct_id`.

That change's Decision 15 descoped the two `account.*` auth events:

- `account.signup.completed` fired at the same instant as `user.created` (`user_uc.go` already publishes `SubjectUserCreated` on user creation, and the consumer already forwards it as `user.created`). A second event would double-count signups.
- `account.login` had no clean signal. The existing `pre_access_token` webhook handler (`backend/internal/adapter/webhook/pre_access_token_handler.go`) fires on **every access-token mint, including silent refresh-token grants**, so emitting `account.login` there over-counts logins.

The product owner has reversed the *deferral* of `account.login` (it is the primary returning-active-user signal for retention cohorts). The reasoning that a refresh is not a login, and that signup must not be double-counted, still holds. This change must satisfy the owner's request without regressing analytics correctness.

The Zitadel webhook already in production is an Actions v2 **Target** invoked with a `PAYLOAD_TYPE_JWT` body: the request body is a JWT whose private claims carry the Actions v2 function payload (`user`, `org`, …). The existing handler verifies that JWT against a webhook-specific audience and reads nested fields (e.g. `user.human.email`). Any login signal must be derivable from this same payload, or from a different Action invocation point Zitadel offers.

**Unverified-assumption hazard (the reason for the spike below).** The production `pre_access_token` handler (`pre_access_token_handler.go`) models the payload as **user/org resource context** only — concretely `user.human.email`. It carries *who* the token is for, not *how* this particular grant was obtained. Whether the `pre_access_token` Actions v2 payload also exposes an OIDC *grant* discriminator — `amr`, a fresh `auth_time`, or an explicit refresh-token-grant indicator — is **NOT verified**. The shape of the existing payload (resource context, no grant context) is strong evidence those fields are ABSENT. This is load-bearing: if they are absent, a handler that "discriminates fresh-vs-refresh" on this payload has nothing to discriminate on, and degrades into one of two failure modes — emit `account.login` on every mint (the over-count Decision 15 deferred the event to avoid), or, under a "suppress when uncertain" rule, emit `account.login` on every mint as *uncertain* and therefore emit **zero** (an unmet goal with no signal). Neither is acceptable. The design below therefore makes verifying this assumption the **first, gating** step, and makes the structurally-login-specific session Action the **primary** design.

## Goals / Non-Goals

**Goals**

- Emit `account.login` exactly once per **user-initiated login**, attributed to the platform `UserId`.
- Guarantee a token **refresh** does NOT emit `account.login`.
- Keep the analytics path non-fatal and non-blocking on the login/token-issuance critical path.
- Resolve `account.signup.completed` without emitting a duplicate of `user.created`.
- Reuse the established publisher → NATS subject → `analytics-consumer` `Handle*` → PostHog pattern; do not call PostHog from the webhook handler directly.

**Non-Goals**

- No new Connect-RPC, no proto change, no DB schema change.
- No frontend emission of `account.login` (BE-sourced / trust-critical per the catalogue).
- No backfill of historical logins; instrumentation is forward-only.
- No reopening of the broader analytics taxonomy beyond these two account events.

## Decisions

### Decision 0 (gating): Spike the actual `pre_access_token` payload BEFORE choosing the login signal

This change does not begin with implementation. It begins with a **payload spike** that resolves the unverified assumption above: does the `pre_access_token` Actions v2 payload, as delivered on **dev Zitadel**, actually expose a usable fresh-vs-refresh discriminator (`amr`, a fresh `auth_time`, or an explicit refresh-token-grant indicator)?

Concretely: temporarily dump the full decoded private-claims payload from the existing handler on a dev Zitadel instance, exercise both flows — a fresh interactive login AND a silent `refresh_token` grant — and compare the two payloads for any field that reliably differs between them.

The spike has exactly two outcomes, and it **gates** which design ships:

- **Outcome A — a reliable discriminator IS present.** The `pre_access_token` payload contains a field that deterministically separates fresh auth from refresh. Then the option in Decision 1 (extend the existing webhook) is permitted, because the discrimination is real rather than assumed.
- **Outcome B — no reliable discriminator is present** (the expected outcome, given the resource-context shape of the production payload). Then the `pre_access_token` webhook **cannot** carry login semantics, and the session-created Action (Decision 1, primary) is the only sound source.

This is a **build-time** decision made once from spike evidence — never a per-request runtime guess. The spike output (the two payloads and the diff) is the recorded justification for the path taken.

### Decision 1: PRIMARY — emit `account.login` from a Zitadel session-created Action; use the `pre_access_token` webhook ONLY if the spike proves a discriminator exists

Two candidate signals were considered:

- **(i) A dedicated Zitadel *session-created* Action (PRIMARY).** A session is created on a user-initiated login and **structurally cannot fire on a silent `refresh_token` grant** — a refresh reuses the existing session and creates no new one. This makes the signal login-specific *by construction*: there is nothing to discriminate, so there is no fresh-vs-refresh ambiguity to get wrong. It needs net-new Zitadel Action configuration (a session-created Target, its own webhook audience, a second handler), but that cost buys correctness that does not depend on an unverified payload shape.
- **(ii) Reuse the existing `pre_access_token` webhook and discriminate fresh-auth vs refresh (CONDITIONAL — only if the spike's Outcome A holds).** The existing Target, its JWT-audience validator, DI wiring, and deployment are already in production on the login path, so reusing them is cheaper *if and only if* the payload actually exposes a grant discriminator (`amr` / fresh `auth_time` / refresh indicator). Per Decision 0 this is unverified and, given the production payload models only `user.human.email` (resource context, not grant context), is expected to be **false**. This option is therefore conditional on the spike, not the default.

**Chosen: (i) — the session-created Action is PRIMARY.** Rationale: the session-created hook is immune to the refresh ambiguity by construction, so it satisfies the goal regardless of how the `pre_access_token` payload is shaped. Option (ii) is selected only if Decision 0's spike yields Outcome A (a real discriminator); otherwise it is structurally unable to separate login from refresh and is discarded. We deliberately reverse the cheaper-reuse default in favour of the signal that cannot silently under- or over-count.

**No runtime "suppress when uncertain" rule.** An earlier framing suppressed the event at runtime whenever discrimination was uncertain. That is rejected: on a payload with no discriminator, *every* request is uncertain, so the rule emits **zero** `account.login` events — an unmet goal that ships silently with no error and no signal to detect it. Uncertainty about whether a payload can discriminate at all is resolved **once, at build time, by Decision 0's spike**, not re-litigated per request. The shipped handler — whichever source it uses — operates on a signal already proven login-specific; it does not guess.

### Decision 2: `sub → UserId` lookup on the login path

`Enqueue` needs the platform `UserId`; the Action payload carries the Zitadel `sub` (the IdP subject). The handler resolves `sub → UserId` via the existing `UserUseCase.GetByExternalID` (already defined in `user_uc.go`, "retrieves a user by identity provider ID (Zitadel sub claim)"). The lookup runs only on the login signal chosen by Decision 1 — which, under the primary session-created Action, fires only on a user-initiated login and never on refresh, so refreshes incur no extra query at all. The resolved `UserId` becomes the NATS event payload's `user_id` and ultimately the PostHog `distinct_id`. If the lookup fails (user not yet provisioned, or transient error), the handler logs and skips the analytics emission — it never fails the login / token-issuance flow.

### Decision 3: `account.signup.completed` is an alias of `user.created`; no new event is emitted

Per Decision 15's still-valid first half, signup and `user.created` are the same instant. This change emits **no** `account.signup.completed`. `user.created` remains the canonical signup signal (already published by `user_uc.go` and forwarded by `AnalyticsConsumer.HandleUserCreated`). The `EventAccountSignupCompleted` constant is retained only as a documented alias/no-op so dashboards referring to "signup" resolve to `user.created`; no publisher is wired for it. This avoids double-counting signups in any summed funnel.

### Decision 4: Analytics wiring is publish-to-NATS, non-blocking, via a new `ACCOUNT.login` subject and `HandleAccountLogin`

The login handler does **not** call PostHog (consistent with "Connect-RPC handlers / webhook handlers MUST NOT call the PostHog SDK directly"). On a login it publishes a new subject `ACCOUNT.login` (new `ACCOUNT` stream, following the UPPERCASE two-segment convention in `entity/event_data.go`) carrying the resolved `UserId`. The `analytics-consumer` gains `HandleAccountLogin`, which mirrors `HandleUserCreated`: parse the CloudEvent data, skip on nil client / empty `UserId`, then `client.Enqueue(ctx, userID, usecase.EventAccountLogin, properties)`. The publish is fire-and-forget on the login path: a publish failure is logged and swallowed so login latency and success are unaffected. This keeps the login-specificity concern (the source Action, Decision 1) and the delivery concern (forwarding at the consumer) in two clean layers, matching the rest of the analytics backend.

The properties payload stays minimal and non-PII (e.g. `login_method` from the Action payload when available); no email or `sub` is ever placed in properties.

## Risks / Trade-offs

- **[Risk] The `pre_access_token` payload has no fresh-vs-refresh discriminator — so it cannot carry login semantics at all.** The production handler models the payload as resource context (`user.human.email`) with no `amr` / `auth_time` / refresh indicator. If, despite that, the `pre_access_token` webhook were used as the login source, it would either emit `account.login` on every token mint (over-count — the exact failure Decision 15 deferred the event to avoid) or, under a misguided "suppress when uncertain" runtime rule, emit zero (unmet goal, silent). **Mitigation:** this risk is *eliminated by design*, not mitigated at runtime: Decision 0's spike resolves payload capability once at build time, and Decision 1 makes the session-created Action — which structurally never fires on refresh — the primary source. The `pre_access_token` webhook is used only if the spike proves a real discriminator exists (Outcome A). There is no runtime suppression heuristic to get wrong.

- **[Risk] Login-event delivery reliability bounds login-count completeness.** The analytics publish is intentionally best-effort and non-blocking, so a NATS publish failure silently drops that one login event. **Mitigation:** accept eventual under-count for analytics (never block login); the consumer's existing retry/backoff handles PostHog-side transients once the NATS message exists; `analytics_consumer_*` metrics surface drops. Note that under-count here is a *delivery* gap (a genuinely-login event that failed to publish), categorically different from the now-eliminated *discrimination* gap (mis-classifying refresh as login).

- **[Trade-off] The primary session-created Action adds net-new Zitadel/infra surface** (a new Target, a new webhook audience, a second handler) versus reusing the already-deployed `pre_access_token` Target. We accept this cost deliberately: the session-created hook is login-specific by construction, so it meets the goal without depending on an unverified payload shape. Reuse of the existing Target is taken only when the spike (Decision 0) proves it can actually discriminate — paying for cheap reuse with a correctness assumption we have not validated is the trade we refuse.

- **[Trade-off] No `account.signup.completed` event** means any external consumer expecting that literal name must map to `user.created`. Accepted: a single canonical signup signal is strictly better than two names for one instant, and the catalogue documents the alias.
