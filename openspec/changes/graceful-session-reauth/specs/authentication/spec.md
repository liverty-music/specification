## MODIFIED Requirements

### Requirement: Silent token refresh strategy
The frontend SHALL refresh access tokens silently at three points, and SHALL
NOT run a proactive background renewal timer (`automaticSilentRenew` stays
disabled): (1) at boot, if the stored access token is already expired; (2) on
**resume to the foreground** (`visibilitychange` to `visible`), if the stored
access token is expired or within a small skew window of expiry; (3) reactively,
when an RPC returns `Unauthenticated`. All three paths share a single-flight
guard so concurrent triggers perform at most one `signinSilent()` call.

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
