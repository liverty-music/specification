## MODIFIED Requirements

### Requirement: Silent token refresh strategy
The frontend SHALL use on-demand token refresh only. Proactive background refresh (`automaticSilentRenew`) SHALL be disabled. Token refresh occurs at exactly two points: (1) at boot if the stored access token is already expired, (2) when an RPC returns `Unauthenticated`.

**Rationale**: With Zitadel refresh token rotation, proactive background renewal running concurrently with a service worker page reload causes both the old and new page to use the same refresh token, resulting in `RefreshTokenInvalid (400)` and forced logout.

#### Scenario: Boot with valid access token
- **WHEN** the app boots and the stored access token is not expired
- **THEN** the app SHALL proceed without calling `signinSilent()`

#### Scenario: Boot with expired access token
- **WHEN** the app boots and the stored access token is expired
- **THEN** the app SHALL call `signinSilent()` once via `restoreSession()`
- **AND** if `signinSilent()` succeeds, the user session SHALL be restored transparently
- **AND** if `signinSilent()` fails, the user SHALL start the session unauthenticated

#### Scenario: No background timer
- **WHEN** the access token is about to expire during an active session
- **THEN** the app SHALL NOT proactively refresh the token
- **AND** the token SHALL be refreshed on the next RPC call that receives `Unauthenticated`
