## MODIFIED Requirements

### Requirement: Unified Language Preference Resolution

The guest (anonymous-period) language preference SHALL be exposed as
observable application state, unified with the authenticated user's
`preferredLanguage` source. The frontend SHALL NOT read the active guest
language through an unobservable locale lookup at render time for the purpose
of driving UI state; bindings that depend on the current language SHALL
depend on the observable language value. An authenticated user always has a
preferred language, so the system SHALL use it as the effective language
without reading or writing any other source.

#### Scenario: Guest language exposed as observable
- **WHEN** a guest's preferred language is read for display or selection state
- **THEN** it SHALL be sourced from the observable current-language value
  (backed by the anonymous-period `language` localStorage key)
- **AND** a change to the guest language SHALL notify dependent bindings so they
  re-evaluate without a manual mirror or a render-time unobservable locale read

#### Scenario: Unified resolution across auth states
- **WHEN** the current preferred language is read
- **THEN** the system SHALL surface the authenticated user's
  `User.preferredLanguage` for an authenticated user and the anonymous-period
  language for a guest
- **AND** callers SHALL NOT branch on authentication state to choose the source

#### Scenario: NULL preferred_language surfaced and backfilled
- **WHEN** an authenticated user's account is restored
- **THEN** the system SHALL surface the account's `User.preferredLanguage` as the effective language
- **AND** the system SHALL NOT call `UserService.SetPreferredLanguage`

## REMOVED Requirements

### Requirement: Backfill Preferred Language When Missing
**Reason**: A User always has a preferred language; UserUseCase.Create requires one, and no stored User lacks it.
**Migration**: None.
