# Restore session on cold start

## Purpose

Defines user authentication behavior: sign up / sign in, session restoration on cold start, and the server-side session monitoring policy.

## Requirements

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

### Requirement: The remembered account is restored on launch

On every launch with a signed-in session, the app SHALL restore the fan's account from the account remembered for the signed-in identity (UserUseCase.Get) before it makes any other per-fan request. When the account has no preferred language, the app SHALL set it to the app's current display language (UserUseCase.UpdatePreferredLanguage) without asking the fan. Once the account's preferred language is in use, the language the app kept on the device before sign-in is dropped, and the account's language wins from then on.

#### Scenario: Reopen with a remembered account

- **WHEN** a signed-in fan reopens the app
- **THEN** the fan's follows, home and language are those of their account

#### Scenario: Account without a language

- **WHEN** a signed-in fan whose account has no preferred language opens the app in Japanese
- **THEN** the account's preferred language becomes `ja`

#### Scenario: Language chosen on another device

- **WHEN** a fan's account language is `en` and the device kept `ja` from before sign-in
- **THEN** after the next launch the app is shown in English
