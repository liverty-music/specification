# Language Resolution

## Purpose

Persists each authenticated user's display language in the backend database so language is consistent across devices and browser sessions. Defines the proto-surface (entity field, Create capture, UpdatePreferredLanguage RPC), the storage semantics (NULL = "not yet set by client"), and the repository scan contract that prevents NULL-column reads from masquerading as `not_found` / `already_exists` at the wire boundary.

## Requirements

### Requirement: Unified Language Preference Resolution

The guest (anonymous-period) language preference SHALL be exposed as
observable application state, unified with the authenticated user's
`preferredLanguage` source. The frontend SHALL NOT read the active guest
language through an unobservable locale lookup at render time for the purpose
of driving UI state; bindings that depend on the current language SHALL
depend on the observable language value. The system SHALL also handle an
authenticated user whose backend preferred-language value is NULL (historical
rows not yet backfilled) by surfacing the detected locale as the effective
language and backfilling the server value via `UserService.UpdatePreferredLanguage`;
this fallback path is independent of the guest-data reconciliation, which
only fires when guest data is present in localStorage.

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
- **WHEN** the authenticated user's `User.preferredLanguage` is NULL
- **THEN** the system SHALL surface the detected locale as the effective language
- **AND** the system SHALL backfill the server value via
  `UserService.UpdatePreferredLanguage`, preserving the current
  `user-hydration-task` behavior
- **AND** this SHALL occur whether or not any guest data exists in localStorage
