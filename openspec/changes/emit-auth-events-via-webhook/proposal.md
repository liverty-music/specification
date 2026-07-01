## Why

The archived `introduce-analytics-tool` change shipped the full conversion funnel but deliberately descoped its two account-auth signals (Decision 15): `account.signup.completed` was redundant with the already-emitted `user.created`, and `account.login` had no clean backend hook — the only login-adjacent touchpoint, the `pre_access_token` webhook, fires on *every* access-token mint including silent refresh-token grants, so emitting there over-counts logins.

The product owner now wants login instrumented anyway: `account.login` is the single best **active-user / returning-user signal** for retention cohorts (D7/D30 by signup month already exist, but they need a recurring "this user came back" event to be meaningful). Decision 15's *deferral* is reversed; its *reasoning* is not. This change therefore MUST solve the over-count problem (a refresh is not a login) and MUST avoid re-introducing the signup redundancy — emitting a misleading login count or a double-counted signup is worse than emitting nothing.

## What Changes

- Emit `account.login` server-side **once per user-initiated login**, attributed to the platform `UserId` (UUID), explicitly NOT on token refresh.
- Adopt Zitadel's **official Actions v2 best practice** as the single implementation path: register an Actions v2 **Execution** on the `response` side of `/zitadel.session.v2.SessionService/CreateSession`, invoking a webhook **Target** that points at a new backend handler. This is login-specific *by construction* — the OIDC `refresh_token` grant mints a new access token "without user interaction" and does NOT call `CreateSession`, so subscribing to `CreateSession` fires once per user-initiated login and never on refresh. There is nothing to discriminate, no payload spike, and no runtime suppression.
  - Docs backing this pattern: [Advanced Session Management with Actions V2](https://zitadel.com/blog/session-management-actions-v2), [Actions v2 concepts](https://zitadel.com/docs/concepts/features/actions_v2), [CreateSession API ref](https://zitadel.com/docs/reference/api/session/zitadel.session.v2.SessionService.CreateSession), [OIDC endpoints (refresh_token grant)](https://zitadel.com/docs/apis/openidoauth/endpoints). Our Zitadel is v4.7.1+, so Actions v2 Executions are GA.
- Verify the webhook body the same way the deployed `pre_access_token` handler does — the Target is `PAYLOAD_TYPE_JWT` and the backend validates the JWT signature against the Zitadel instance JWKS (`WebhookValidator`). No shared HMAC secret is introduced; JWKS signature + the private-only webhook listener is the security boundary, identical to the existing Target.
- Read the login user identifier from the Actions payload at `request.checks.user.userId` (present on the `response`-side payload, which carries both `request` and `response`), then map that Zitadel `sub` to the platform `UserId` via the existing `GetByExternalID` lookup, because `AnalyticsClient.Enqueue` requires the platform `UserId` as `distinct_id` (never the IdP `sub`).
- Wire the analytics path **non-fatal and non-blocking**: the handler publishes a domain event to NATS and lets the `analytics-consumer` forward it to PostHog, matching the existing publisher → consumer → PostHog pattern. A failure on the analytics path MUST NOT break session creation / login.
- Add a new NATS subject (`ACCOUNT.login`) on a new `ACCOUNT` stream and a corresponding `analytics-consumer` `HandleAccountLogin` method that forwards it as the `account.login` catalogue event.
- Resolve `account.signup.completed` by **aliasing signup analytics to the existing `user.created`** — no new event is emitted. The unused `EventAccountSignupCompleted` constant remains a no-op alias documented as such; `user.created` is the canonical signup signal.

## Capabilities

### Modified Capabilities

- `product-analytics`: account authentication events are now emitted server-side. `account.login` is login-specific (one event per user-initiated login, never on token refresh) and attributed to the platform `UserId`; signup continues to be represented by `user.created` with no duplicate `account.signup.completed`.

## Impact

- **New backend webhook handler**: a `CreateSession` Actions v2 Target handler (`backend/internal/adapter/webhook/`) validates the `PAYLOAD_TYPE_JWT` body via the existing `WebhookValidator` (JWKS), reads `request.checks.user.userId`, and publishes a non-blocking `account.login` analytics event. It registers a new route on the existing internal-only webhook listener and needs DI wiring for the `EventPublisher` and the `sub → UserId` lookup.
- **New Zitadel Actions v2 resources (cloud-provisioning)**: a new `CreateSession` Target (`PAYLOAD_TYPE_JWT`, `interruptOnError: false` so analytics never blocks login) plus a `response`-condition Execution on `/zitadel.session.v2.SessionService/CreateSession`. The current dynamic resources support only `function` and `request` conditions, so a new `ZitadelExecutionResponse` dynamic resource (`condition: { response: { method } }`) is added.
- **New NATS subject + stream + consumer method**: `ACCOUNT.login` subject on a new `ACCOUNT` stream (streams.go) and `AnalyticsConsumer.HandleAccountLogin`, plus the matching KEDA trigger (stream `ACCOUNT`, consumer `ACCOUNT_login`) in the cloud-provisioning consumer scaledobject base.
- **New user lookup on the login path**: `sub → UserId` via the existing `GetByExternalID`, run only on a user-initiated login (never on refresh, which does not reach this handler).
- **No new RPC, no proto change, no DB schema change**: this rides the existing Zitadel Actions webhook + NATS + analytics-consumer + PostHog infrastructure introduced by `introduce-analytics-tool`.
- **No frontend change**: `account.login` is BE-sourced / trust-critical per the event catalogue; the frontend does not emit it.
- **Event catalogue**: `account.login` moves from "defined but no publisher" to "emitted"; `account.signup.completed` is documented as an alias of `user.created` (not separately emitted).
- **Risk surface**: the over-count/discrimination risk is *eliminated by design* — `CreateSession` structurally cannot fire on refresh. The remaining risks are (a) best-effort delivery bounding login-count completeness (acceptable under-count) and (b) a login flow that attaches the user via `loginName` or a later `SetSession` rather than `checks.user.userId`, which the handler skips-and-logs. Both are addressed in design.md.
