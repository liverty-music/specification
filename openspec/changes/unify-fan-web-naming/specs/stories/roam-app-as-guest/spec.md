# Spec Delta

## MODIFIED Requirements

### Requirement: Global Auth Hook

The system SHALL provide a global authentication lifecycle hook (`AuthHook`) that gates SPA route loads based on authentication state only. The hook SHALL NOT enforce onboarding step ordering — there is no step machine and no ordinal `tutorialStep` comparison. For guests (unauthenticated users) the hook SHALL permit free roam across application routes (soft gate); account-only features SHALL be hidden at point of use per `guest-mode-access` rather than blocked by navigation. The timetable SHALL be reachable at any onboarding state; a guest with no follows SHALL be guided by an in-page empty-state call-to-action toward discovery, not by a guard redirect.

#### Scenario: Authenticated user navigates to any route

- **WHEN** a user has `isAuthenticated = true`
- **THEN** the system SHALL allow the route component to load
- **AND** no onboarding-based restrictions SHALL be applied

#### Scenario: Public route is always allowed

- **WHEN** a route has `data.auth === false` (e.g. Welcome, About, auth callback, legal pages)
- **THEN** the system SHALL allow the route to load regardless of authentication or onboarding state

#### Scenario: Guest navigates to an application route

- **WHEN** a user has `isAuthenticated = false`
- **AND** the target route is an application route (e.g. timetable, discovery, my-artists, tickets, settings)
- **THEN** the system SHALL allow the route to load (guest free roam / soft gate)
- **AND** the system SHALL NOT redirect based on any onboarding step
- **AND** account-only features on the destination SHALL be hidden at point of use per `guest-mode-access`

#### Scenario: Guest with no follows lands on the timetable

- **WHEN** a user has `isAuthenticated = false`
- **AND** the user navigates to `/timetable` with zero followed artists
- **THEN** the system SHALL allow the timetable to load
- **AND** the timetable SHALL present an empty-state call-to-action pointing to discovery
- **AND** the system SHALL NOT redirect the user away from the timetable
