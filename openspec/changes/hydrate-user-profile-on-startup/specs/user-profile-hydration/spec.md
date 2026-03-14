## ADDED Requirements

### Requirement: User profile hydration at app startup

The frontend SHALL load the authenticated user's backend profile into a centralized in-memory store during application startup, making the User entity available to all routes without per-page fetching.

#### Scenario: Authenticated page load or reload

- **WHEN** the Aurelia application starts (page load or browser reload)
- **AND** the OIDC token is present and valid (`authService.isAuthenticated === true`)
- **THEN** the system SHALL call `UserService.Get` RPC before any route renders
- **AND** the system SHALL store the returned `User` entity in `UserService.current`

#### Scenario: Unauthenticated or guest startup

- **WHEN** the Aurelia application starts
- **AND** the user is not authenticated
- **THEN** the system SHALL NOT call `UserService.Get`
- **AND** `UserService.current` SHALL remain `undefined`

### Requirement: User profile hydration after auth callback

The frontend SHALL load the authenticated user's backend profile immediately after a successful sign-in or sign-up, before navigating to the destination route.

#### Scenario: Sign-in via auth callback

- **WHEN** an existing user completes OIDC sign-in
- **AND** the auth callback has successfully processed the token
- **AND** `provisionUser()` has completed
- **THEN** the system SHALL call `UserService.ensureLoaded()`
- **AND** the system SHALL store the returned `User` entity in `UserService.current`
- **AND** navigation to the destination route SHALL occur only after `ensureLoaded()` resolves

#### Scenario: Sign-up via auth callback

- **WHEN** a new user completes OIDC sign-up during onboarding
- **AND** the auth callback has processed the token and provisioned the user
- **THEN** the system SHALL call `UserService.ensureLoaded()`
- **AND** the returned `User` entity SHALL include the home area submitted during `provisionUser()`

### Requirement: Idempotent profile loading

The `ensureLoaded()` method SHALL be idempotent — multiple calls SHALL NOT result in redundant RPC requests.

#### Scenario: Profile already loaded

- **WHEN** `UserService.ensureLoaded()` is called
- **AND** `UserService.current` is already populated (not undefined)
- **THEN** the system SHALL return the existing `current` value immediately
- **AND** the system SHALL NOT make a `UserService.Get` RPC call

#### Scenario: Profile not yet loaded

- **WHEN** `UserService.ensureLoaded()` is called
- **AND** `UserService.current` is undefined
- **AND** `authService.isAuthenticated` is true
- **THEN** the system SHALL call `UserService.Get` RPC
- **AND** SHALL store the result in `UserService.current`

### Requirement: Graceful degradation on hydration failure

The startup hydration SHALL NOT prevent the application from loading if the backend is unreachable or returns an error. The system SHALL log the failure and continue with `UserService.current` remaining `undefined`.

#### Scenario: Backend unreachable during startup hydration

- **WHEN** `UserService.ensureLoaded()` is called during `AppTask.activating()`
- **AND** the RPC call fails (network error, timeout, or server error)
- **THEN** the system SHALL catch the error
- **AND** the system SHALL log a warning with the error details
- **AND** `UserService.current` SHALL remain `undefined`
- **AND** the application SHALL continue to render normally

### Requirement: Write-through on user mutation

When the user's profile is mutated via an RPC, the in-memory `current` state SHALL be updated with the response, without requiring a separate `Get` call.

#### Scenario: Home area updated

- **WHEN** an authenticated user calls `UserService.updateHome()` successfully
- **THEN** the system SHALL update `UserService.current` with the `User` entity returned in the RPC response
- **AND** subsequent reads of `UserService.current.home` SHALL reflect the new home area

### Requirement: Profile cleared on sign-out

The system SHALL clear the in-memory user profile when the user signs out, preventing stale data from being accessible to a subsequent session.

#### Scenario: User signs out

- **WHEN** the user initiates sign-out
- **THEN** the system SHALL set `UserService.current` to `undefined`
- **AND** the system SHALL perform this cleanup before the OIDC sign-out redirect
