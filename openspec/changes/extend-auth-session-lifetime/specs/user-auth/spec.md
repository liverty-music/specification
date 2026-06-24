## ADDED Requirements

### Requirement: Session Restoration on App Cold Start

The system SHALL transparently restore an authenticated session when the app cold-starts (including PWA relaunch) with a stored user whose access token has expired but whose refresh token is still valid. On boot, the auth service SHALL detect the expired-access-token condition and attempt a silent refresh-token renewal (`signinSilent()`) BEFORE resolving auth readiness, so that route guards and UI never observe a transient signed-out state for a user who can be silently re-authenticated.

This requirement exists because `oidc-client-ts` `automaticSilentRenew` only schedules renewal for a not-yet-expired access token; when the app starts with an already-expired access token it abandons renewal without consulting the refresh token (oidc-client-ts issue #2012). The boot-time silent renewal closes that gap.

#### Scenario: Reopen after access token expiry with valid refresh token

- **WHEN** the app cold-starts and a stored user is loaded whose access token is expired
- **AND** the user's refresh token is still within its idle and absolute expiration windows
- **THEN** the system SHALL invoke `signinSilent()` to obtain new tokens via the refresh-token grant
- **AND** the system SHALL resolve the auth-readiness promise only after the silent renewal attempt settles
- **AND** the resulting auth state SHALL be authenticated
- **AND** the UI SHALL NOT render a signed-out state for the elapsed gap

#### Scenario: Reopen after refresh token has expired

- **WHEN** the app cold-starts and a stored user is loaded whose access token is expired
- **AND** the user's refresh token is no longer valid (idle or absolute expiration exceeded)
- **THEN** the silent renewal attempt SHALL fail
- **AND** the system SHALL resolve to an unauthenticated state
- **AND** the user SHALL be treated as signed out (legitimate re-authentication required)

#### Scenario: Reopen within access token validity

- **WHEN** the app cold-starts and a stored user is loaded whose access token is still valid
- **THEN** the system SHALL NOT trigger a boot-time silent renewal
- **AND** the system SHALL resolve to the authenticated state using the existing tokens

### Requirement: Server-Side Session Monitoring Disabled

The system SHALL disable OIDC server-side session monitoring (`monitorSession`) in all environments. The hidden `check_session_iframe` polling mechanism is incompatible with the self-hosted Zitadel instance, which serves that endpoint with `Content-Security-Policy: frame-ancestors 'none'`, causing the embedded iframe to fail and `oidc-client-ts` to emit spurious `userUnloaded` events. Detection of session changes made outside the app (e.g. logout at the identity provider) is deferred to the next token refresh rather than real-time iframe polling.

#### Scenario: Session monitoring is off regardless of environment

- **WHEN** the OIDC `UserManager` is configured at app startup
- **THEN** `monitorSession` SHALL be `false` in every environment (dev and prod)
- **AND** the system SHALL NOT load the Zitadel `check_session_iframe`
- **AND** the system SHALL NOT emit `userUnloaded` events triggered by iframe session polling
