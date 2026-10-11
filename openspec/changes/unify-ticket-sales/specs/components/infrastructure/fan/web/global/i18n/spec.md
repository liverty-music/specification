# Spec Delta

## MODIFIED Requirements

### Requirement: Unified Language Preference Resolution

The guest (anonymous-period) language preference SHALL be exposed as
observable application state, unified with the authenticated user's
`preferredLanguage` source. The frontend SHALL NOT read the active guest
language through an unobservable locale lookup at render time for the purpose
of driving UI state; bindings that depend on the current language SHALL
depend on the observable language value. The system SHALL also handle an
authenticated user whose backend preferred-language value is NULL (historical
rows not yet backfilled) by surfacing the detected locale as the effective
language and backfilling the server value via `UserService.SetPreferredLanguage`;
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
  `UserService.SetPreferredLanguage`, preserving the current
  `user-hydration-task` behavior
- **AND** this SHALL occur whether or not any guest data exists in localStorage

### Requirement: Language Switching

The system SHALL re-render all translated strings when the active locale
changes without requiring a page reload, using a shared utility for changing
the active locale that selects the correct persistence path based on the
caller's authentication state, so components do not duplicate this logic.
The persistence target SHALL depend on the authentication state: anonymous
changes persist to `localStorage`; authenticated changes persist to the
backend user row via `UserService.SetPreferredLanguage`.

#### Scenario: Switching language mid-session as an anonymous user
- **WHEN** an unauthenticated user changes the language preference (e.g., from the Welcome page language selector)
- **THEN** all `t`-bound template strings SHALL immediately update to the new locale
- **AND** the `language` key in localStorage SHALL be updated
- **AND** the system SHALL NOT issue any backend RPC for the change
- **AND** date/number formatters SHALL use the new locale for subsequent renders

#### Scenario: Switching language mid-session as an authenticated user
- **WHEN** an authenticated user changes the language preference (e.g., from the Settings page)
- **THEN** the system SHALL call `UserService.SetPreferredLanguage` with the new locale
- **AND** on success, the system SHALL call `i18n.setLocale` so all `t`-bound template strings update immediately
- **AND** the system SHALL NOT read or write `localStorage['language']` for this change
- **AND** date/number formatters SHALL use the new locale for subsequent renders

#### Scenario: Authenticated language switch RPC failure
- **WHEN** the `SetPreferredLanguage` RPC fails (network, server error)
- **THEN** the active locale SHALL end at the value it held before the change was attempted (the implementation MAY apply the new locale optimistically and revert on failure; the user-observable end-state SHALL be unchanged)
- **AND** the system SHALL surface a user-visible error notification (Snack)

#### Scenario: Anonymous caller path
- **WHEN** any component calls the shared language-change utility while unauthenticated
- **THEN** the utility SHALL call `i18n.setLocale(lang)` and `localStorage.setItem('language', lang)`
- **AND** the utility SHALL NOT issue any backend RPC

#### Scenario: Authenticated caller path
- **WHEN** any component calls the shared language-change utility while authenticated
- **THEN** the utility SHALL call `UserService.SetPreferredLanguage` first
- **AND** on success, the utility SHALL call `i18n.setLocale(lang)`
- **AND** the utility SHALL NOT touch `localStorage['language']`

#### Scenario: Used by both Welcome and Settings
- **WHEN** the Welcome page (anonymous context) and Settings page (authenticated context) both change language
- **THEN** they SHALL both call the same shared utility
- **AND** the utility SHALL route persistence appropriately for each context

### Requirement: Backfill Preferred Language When Missing

When the hydrated user profile has no preferred language set (NULL legacy row), the system SHALL backfill the DB by persisting the currently effective locale before continuing.

#### Scenario: Hydrated profile has no preferred language

- **WHEN** `UserService.ensureLoaded()` resolves
- **AND** `UserService.current.preferredLanguage` is absent (proto `optional` field not present)
- **THEN** the system SHALL call `UserService.setPreferredLanguage(I18N.getLocale())`
- **AND** on success, `UserService.current.preferredLanguage` SHALL match the value sent
- **AND** the active i18n locale SHALL remain unchanged (no flicker because the value matched what was already effective)

#### Scenario: Backfill RPC failure is non-fatal

- **WHEN** the backfill `SetPreferredLanguage` RPC fails
- **THEN** the system SHALL log a warning
- **AND** the application SHALL continue to render with the current locale
- **AND** the next hydration cycle SHALL retry the backfill (because the DB still holds NULL)
