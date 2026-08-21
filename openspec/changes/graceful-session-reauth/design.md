## Context

The frontend (`shared/services/auth-service.ts`) is a browser-based OAuth
client (oidc-client-ts v3.4.1) against a self-hosted Zitadel. Instance token
lifetimes: access 30m, refresh idle 30d / absolute 90d. `automaticSilentRenew`
and `monitorSession` are both disabled (documented in the `authentication` and
`user-auth` specs) because Zitadel rotates refresh tokens and the self-hosted
`check_session_iframe` is served with `frame-ancestors 'none'`.

Investigation (2026-08-21, server logs + browser console) established:

- Zitadel refreshes succeed (all `/oauth/v2/token` return 200; a `refreshToken`
  grant for the admin org user succeeded live). Refresh is NOT broken at the IdP.
- The on-`Unauthenticated` reactive refresh+retry works: creating `org-test-11`
  after ~42m idle produced `Create → 401 → Auth state updated (refresh) → org
  created` in one pass.
- The user-visible problem is the **cold-start 401**: with no resume-time
  refresh, the token goes cold during idle, so the first foreground RPC 401s.
  The browser logs that 401, and the admin route renders the raw error text
  (`"exp" not satisfied`). Reactive recovery is also occasionally flaky.
- fan-web does not show this because it re-fetches constantly and has a
  `visibilitychange` resume-revalidator that warms the token before the user
  acts; admin/organizer have neither.

## Goals / Non-Goals

**Goals:** eliminate the cold-start 401 for idle→resume→action; never show a raw
auth error; do it uniformly in the shared auth service so all three entries
benefit; keep the refresh-token-rotation race closed.

**Non-Goals:** enabling `automaticSilentRenew` or any background timer; a BFF /
server-side token model; changing Zitadel token lifetimes; reworking the
consumer's resume-revalidator (it stays and is complementary).

## Decisions

**D1 — Refresh on resume (`visibilitychange`), not on a timer.** The gap is
"token went cold while the tab was idle/backgrounded". A background timer cannot
close it: oidc-client-ts `automaticSilentRenew` abandons renewal once the token
is already expired (issue #2012), and browsers throttle/suspend background-tab
timers so the timer would not fire during idle anyway. The boot-time
`restoreSession()` already refreshes-if-expired-before-any-call and is exactly
why a manual reload fixes the error. So the fix generalizes that boot behavior to
every foreground resume: on `visibilitychange` to `visible`, if the access token
is expired (or within a small skew, e.g. ~60s), run one `signinSilent()` before
the next RPC. This is the ecosystem-recommended "refresh on resume / before-use"
pattern (cf. angular-auth-oidc-client silent renew, oidc-spa
`renewTimeBeforeTokenExpiresInSeconds`), adapted to our iframe-less, timer-less
constraints.

**D2 — Single-flight guard, shared across all three refresh paths.** The reason
`automaticSilentRenew` was disabled is the refresh-token rotation race (two
concurrent `signinSilent()` calls spend the same rotating refresh token; the
second gets `RefreshTokenInvalid`). The resume refresh MUST NOT reintroduce it.
Reuse a single module/service-level in-flight promise so boot, resume, and
on-`Unauthenticated` refreshes coalesce into at most one concurrent
`signinSilent()`. Because resume fires only on an explicit event (at most once
per resume) and coalesces with any in-flight refresh, it does not race a
service-worker reload the way a free-running timer did.

**D3 — Recoverable auth errors are invisible; unrecoverable ones show a neutral
state.** Today a token-expiry `Unauthenticated` that the interceptor cannot
recover throws, and route error handlers render `err.rawMessage` — the raw
`"exp" not satisfied`. Change the contract: successful refresh+retry is silent
(already the intent); on unrecoverable expiry the app shows a neutral "session
expired — signing you back in" state and routes to re-auth, never the transport
string. This applies both to the interceptors' failure branch and to any route
`toUserMessage`-style mapper, so an `Unauthenticated` code never maps to raw text.

**D4 — Shared service, per-entry activation.** Implement in
`shared/services/auth-service.ts` (the single OIDC surface used by all three
entries) so consumer/admin/organizer get identical behavior. The consumer's
`resume-revalidator` (data revalidation) is orthogonal and remains; the new
resume refresh operates at the auth layer, below it.

## Risks / Trade-offs

- **Double-fire on resume + first RPC.** If the user resumes and immediately
  triggers an RPC, the resume refresh and a reactive refresh could both start.
  The single-flight guard (D2) makes them coalesce — no double refresh-token
  spend.
- **Skew window tuning.** Too large a pre-expiry skew wastes refreshes; too
  small risks a cold RPC right after resume. ~60s is a safe default (well under
  the 30m access lifetime).
- **Multi-tab.** Two visible tabs resuming simultaneously could each refresh.
  The per-tab single-flight guard prevents intra-tab races; cross-tab remains as
  today (the existing on-`Unauthenticated` path already tolerates it, and Zitadel
  rotation means the loser simply re-refreshes). Cross-tab leader election is a
  possible future hardening but is out of scope.

## Migration Plan

1. Add the resume-time refresh + shared single-flight guard to
   `shared/services/auth-service.ts`; wire a `visibilitychange` listener at
   bootstrap for each entry (or in the shared service).
2. Route `Unauthenticated` through a graceful mapper so no raw transport text is
   rendered; unrecoverable → neutral "session expired" + re-auth.
3. Unit-test: resume-with-expired → one refresh; resume-with-valid → no refresh;
   concurrent triggers → single `signinSilent()`; unrecoverable → neutral state,
   no raw string.
4. Verify in prod on the admin console: idle > 30m → resume → create an Organizer
   with no 401 in the console and no error text.
- Rollback: additive listener + mapper; remove to revert to on-`Unauthenticated`-only.
