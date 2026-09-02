## MODIFIED Requirements

### Requirement: Silent token refresh strategy
The frontend SHALL refresh access tokens silently at three points, and SHALL
NOT run a proactive background renewal timer (`automaticSilentRenew` stays
disabled): (1) at boot, if the stored access token is already expired; (2) on
**resume to the foreground** (`visibilitychange` to `visible`), if the stored
access token is expired or within a small skew window of expiry; (3) reactively,
when an RPC returns `Unauthenticated`.

**Reactive refresh contract**: when an authenticated caller's RPC returns
`Unauthenticated`, the app SHALL perform a silent refresh and then **retry the
original request once** with the new access token. The retry is bounded to a
single attempt per request: if the retried request also returns
`Unauthenticated`, the app SHALL NOT refresh-and-retry again (no unbounded
loop) — it SHALL treat the session as unrecoverable (see *Graceful session
re-authentication*).

**Single-flight**: all three refresh points, and every concurrent trigger within
them, SHALL share **one** in-flight refresh so that at most one `signinSilent()`
runs at a time. This includes the boot-time restore and the reactive interceptor:
an early RPC that 401s while boot-time restore is still in flight MUST join the
in-flight refresh rather than start a second, concurrent `signinSilent()`. This
single-flight guarantee is the direct antidote to the Zitadel refresh-token
rotation race the disabled background timer was avoiding.

**Rationale**: With Zitadel refresh token rotation, a *background timer* running
concurrently with a service-worker page reload causes both the old and new page
to use the same refresh token, resulting in `RefreshTokenInvalid (400)` and
forced logout — so the timer stays off. The resume-time refresh is NOT a timer:
it fires only on an explicit foreground-resume event, at most once per resume,
through the shared single-flight guard, so it does not reintroduce the rotation
race. It closes the gap the timer cannot cover — `oidc-client-ts`
`automaticSilentRenew` abandons renewal once the access token is already expired
(issue #2012) and browsers throttle background-tab timers, so neither would
refresh a token that went cold while the tab was idle. Resume-time refresh warms
the token *before* the user's next action, mirroring the boot-time restore that
already makes a manual reload recover the session.

#### Scenario: Boot with valid access token
- **WHEN** the app boots and the stored access token is not expired
- **THEN** the app SHALL proceed without calling `signinSilent()`

#### Scenario: Boot with expired access token
- **WHEN** the app boots and the stored access token is expired
- **THEN** the app SHALL call `signinSilent()` once via `restoreSession()`
- **AND** if `signinSilent()` succeeds, the user session SHALL be restored transparently
- **AND** if `signinSilent()` fails, the user SHALL start the session unauthenticated

#### Scenario: Resume from idle with an expired access token
- **WHEN** the app returns to the foreground (`visibilitychange` to `visible`)
  after an idle period
- **AND** the stored user is authenticated but the access token is expired or
  within the skew window of expiry
- **THEN** the app SHALL perform a single silent refresh before the user's next
  RPC
- **AND** if it succeeds, subsequent RPCs SHALL use the fresh token with no
  visible interruption
- **AND** the refresh SHALL be de-duplicated with any in-flight refresh (at most
  one `signinSilent()` for concurrent triggers)

#### Scenario: Resume with a still-valid access token
- **WHEN** the app returns to the foreground and the stored access token is not
  expired and not within the skew window
- **THEN** the app SHALL NOT trigger a resume-time refresh

#### Scenario: No background timer
- **WHEN** the access token is about to expire during an active, foreground session
- **THEN** the app SHALL NOT proactively refresh the token on a timer
- **AND** the token SHALL be refreshed on the next resume event or the next RPC
  that receives `Unauthenticated`, whichever comes first

#### Scenario: Reactive refresh retries the original request once
- **WHEN** an authenticated caller's RPC returns `Unauthenticated`
- **THEN** the app SHALL perform a silent refresh
- **AND** if the refresh succeeds, the app SHALL retry the original request once
  with the new access token
- **AND** the retried request's result SHALL be returned to the caller (a success
  is transparent; the caller never observes the initial `Unauthenticated`)

#### Scenario: Refresh-and-retry is bounded to once per request
- **WHEN** the retried request also returns `Unauthenticated`
- **THEN** the app SHALL NOT trigger another refresh-and-retry for that request
- **AND** the session SHALL be treated as unrecoverable

#### Scenario: Concurrent triggers share one refresh (single-flight)
- **WHEN** multiple refresh triggers occur close together (e.g. several RPCs
  return `Unauthenticated` at once, or a resume event coincides with an
  in-flight boot-time restore)
- **THEN** the app SHALL execute at most one `signinSilent()` call
- **AND** all waiting callers SHALL observe the result of that single refresh

## ADDED Requirements

### Requirement: Graceful session re-authentication
The frontend SHALL NOT surface a raw backend authentication error (for example
the literal string `invalid token: failed to validate token: "exp" not
satisfied`) to the user. When an RPC fails with `Unauthenticated`, the app SHALL
attempt silent recovery (refresh + retry) transparently; a successful recovery
SHALL be invisible to the user. When recovery is not possible (the refresh token
itself is expired or invalid), the app SHALL present a neutral, human-readable
state (for example "your session expired — signing you back in") and route the
user to re-authentication, rather than rendering the transport-level error text.

**Forced-logout cleanup parity**: an involuntary logout triggered by an
unrecoverable `Unauthenticated` SHALL clear session state the same way a
voluntary sign-out does — it SHALL publish the same signed-out signal so that
user-specific caches/stores self-clear. The involuntary and voluntary logout
paths SHALL NOT diverge in what they clean up (a forced logout MUST NOT leave
stale user data behind).

**Return-to preservation**: on an involuntary re-authentication, the app SHALL
preserve where the user was so that, after re-authenticating, the user returns to
the same location rather than a default landing page.

**Unauthenticated caller pass-through**: an `Unauthenticated` response for a
caller that has no session (guest / pre-authentication flows) SHALL NOT trigger a
silent refresh or a forced logout; the error SHALL propagate to the caller so the
flow can handle it locally.

**Cross-context note**: the single-flight guard is per browsing context (per
tab). Concurrent refreshes across separate tabs or a service-worker-reloaded page
remain possible; they are tolerated (Zitadel rotation causes the loser to simply
refresh again) and cross-tab leader election is out of scope for this change.

#### Scenario: Recoverable expiry is invisible
- **WHEN** an RPC returns `Unauthenticated` because the access token expired
- **AND** a silent refresh succeeds and the retried RPC succeeds
- **THEN** the user SHALL NOT see any error text for that RPC

#### Scenario: Unrecoverable expiry shows a neutral state, not the raw error
- **WHEN** an RPC returns `Unauthenticated` and silent refresh fails (refresh
  token expired/invalid)
- **THEN** the app SHALL NOT render the transport-level error string to the user
- **AND** the app SHALL present a neutral "session expired" state and route to
  re-authentication

#### Scenario: Forced logout clears user data like a voluntary sign-out
- **WHEN** an unrecoverable `Unauthenticated` forces a logout
- **THEN** the app SHALL publish the same signed-out signal a voluntary sign-out
  publishes
- **AND** user-specific caches/stores SHALL be cleared
- **AND** no stale user data SHALL remain after the forced logout

#### Scenario: User returns to where they were after involuntary re-auth
- **WHEN** the user is forced to re-authenticate mid-session from a specific
  location
- **AND** they complete re-authentication
- **THEN** the app SHALL return them to that location (not a default landing page)

#### Scenario: Guest 401 propagates without refresh or logout
- **WHEN** an RPC returns `Unauthenticated` for a caller with no established
  session (guest / onboarding)
- **THEN** the app SHALL NOT attempt a silent refresh
- **AND** the app SHALL NOT force a logout/redirect
- **AND** the error SHALL propagate to the caller
