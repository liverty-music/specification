## Why

The archived `introduce-analytics-tool` change shipped the full conversion funnel but deliberately descoped its two account-auth signals (Decision 15): `account.signup.completed` was redundant with the already-emitted `user.created`, and `account.login` had no clean backend hook — the only login-adjacent touchpoint, the `pre_access_token` webhook, fires on *every* access-token mint including silent refresh-token grants, so emitting there over-counts logins.

The product owner now wants login instrumented anyway: `account.login` is the single best **active-user / returning-user signal** for retention cohorts (D7/D30 by signup month already exist, but they need a recurring "this user came back" event to be meaningful). Decision 15's *deferral* is reversed; its *reasoning* is not. This change therefore MUST solve the over-count problem (a refresh is not a login) and MUST avoid re-introducing the signup redundancy — emitting a misleading login count or a double-counted signup is worse than emitting nothing.

## What Changes

- Emit `account.login` server-side **once per user-initiated login**, attributed to the platform `UserId` (UUID), via a Zitadel Actions login signal that is structurally login-specific — explicitly NOT on token refresh.
- **Gate the design on a payload spike first (Decision 0):** before any implementation, dump the actual `pre_access_token` Actions v2 payload on dev Zitadel and check whether it exposes a usable fresh-vs-refresh discriminator (`amr` / `auth_time` / refresh indicator). The production handler models only `user.human.email` (user/org resource context, not OIDC grant context), so this discriminator is expected to be ABSENT.
- **Make the session-created Action the PRIMARY login source** — a session is created on login and cannot be created by a silent `refresh_token` grant, so it is login-specific by construction with nothing to discriminate. Reuse the existing `pre_access_token` webhook with payload discrimination ONLY if the spike proves the needed fields are present. The earlier "discriminate inside the `pre_access_token` handler, suppress at runtime when uncertain" framing is replaced: undiscriminability is resolved once at build time by the spike, not silently suppressed per request (which would emit zero logins and fail the goal with no signal).
- Map the Zitadel `sub` claim carried in the Action payload to the platform `UserId` via the existing `GetByExternalID` lookup, because `AnalyticsClient.Enqueue` requires the platform `UserId` as `distinct_id` (never the IdP `sub`).
- Wire the analytics path into the login handler **non-fatal and non-blocking**: publish a domain event to NATS and let the `analytics-consumer` forward it to PostHog, matching the existing publisher → consumer → PostHog pattern. A failure on the analytics path MUST NOT break token issuance / login.
- Add a new NATS subject (`ACCOUNT.login`) and a corresponding `analytics-consumer` `HandleAccountLogin` method that forwards it as the `account.login` catalogue event.
- Resolve `account.signup.completed` by **aliasing signup analytics to the existing `user.created`** — no new event is emitted. The unused `EventAccountSignupCompleted` constant remains a no-op alias documented as such; `user.created` is the canonical signup signal.

## Capabilities

### Modified Capabilities

- `product-analytics`: account authentication events are now emitted server-side. `account.login` is login-specific (one event per user-initiated login, never on token refresh) and attributed to the platform `UserId`; signup continues to be represented by `user.created` with no duplicate `account.signup.completed`.

## Impact

- **Spike first (gating)**: a throwaway payload dump on dev Zitadel decides the source; the spike output (fresh-login vs refresh payload diff) is the recorded justification for the path taken.
- **New backend login handler (primary path)**: a session-created Zitadel Actions Target handler (`backend/internal/adapter/webhook/`) publishes a non-blocking `account.login` analytics event; it needs a new webhook audience and DI wiring. (If — and only if — the spike proves a discriminator, the existing `pre_access_token` handler is extended instead, reusing its deployed Target.)
- **New NATS subject + consumer method**: `ACCOUNT.login` subject (new `ACCOUNT` stream) and `AnalyticsConsumer.HandleAccountLogin`.
- **New user lookup on the login path**: `sub → UserId` via the existing `GetByExternalID`, run on a user-initiated login only.
- **No new RPC, no proto change, no DB schema change**: this rides the existing Zitadel Actions webhook + NATS + analytics-consumer + PostHog infrastructure introduced by `introduce-analytics-tool` (the primary path adds one session-created Target alongside the deployed `pre_access_token` Target).
- **No frontend change**: `account.login` is BE-sourced / trust-critical per the event catalogue; the frontend does not emit it.
- **Event catalogue**: `account.login` moves from "defined but no publisher" to "emitted"; `account.signup.completed` is documented as an alias of `user.created` (not separately emitted).
- **Risk surface**: the discrimination risk is *eliminated by design* — the primary session-created Action cannot fire on refresh, and the spike (not a runtime heuristic) decides whether the `pre_access_token` payload may be used at all. The remaining risk is best-effort delivery bounding login-count completeness (acceptable under-count). Both are addressed in design.md.
