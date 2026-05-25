## MODIFIED Requirements

### Requirement: Write-through on user mutation

When the user's profile is mutated via an RPC, the in-memory `current` state SHALL be updated with the response, without requiring a separate `Get` call.

#### Scenario: Home area updated

- **WHEN** an authenticated user calls `UserService.updateHome()` successfully
- **THEN** the system SHALL update `UserService.current` with the `User` entity returned in the RPC response
- **AND** subsequent reads of `UserService.current.home` SHALL reflect the new home area

#### Scenario: Preferred language updated

- **WHEN** an authenticated user calls `UserService.updatePreferredLanguage()` successfully
- **THEN** the system SHALL update `UserService.current` with the `User` entity returned in the RPC response
- **AND** subsequent reads of `UserService.current.preferredLanguage` SHALL reflect the new value
- **AND** the system SHALL call `I18N.setLocale()` with the new value so all `t`-bound bindings re-render

---

## ADDED Requirements

### Requirement: Apply Preferred Language to i18n After Hydration

After loading the authenticated user's profile, the system SHALL apply the user's stored preferred language to the active i18n locale, making the DB the source of truth for authenticated sessions.

#### Scenario: Preferred language present in hydrated profile

- **WHEN** `UserService.ensureLoaded()` resolves and `UserService.current.preferredLanguage` is set
- **THEN** the system SHALL call `I18N.setLocale(UserService.current.preferredLanguage)`
- **AND** all `t`-bound template strings SHALL re-render to the resolved locale

#### Scenario: Brief locale flicker on slow networks is acceptable

- **WHEN** the application bootstraps an authenticated user
- **AND** the initial i18n chain (querystring → localStorage → navigator) sets a tentative locale before `ensureLoaded()` resolves
- **THEN** the system MAY render with the tentative locale until the hydration completes
- **AND** the system SHALL switch to the DB-sourced locale as soon as hydration resolves
- **AND** the system SHALL NOT block initial render waiting for hydration

---

### Requirement: Backfill Preferred Language When Missing

When the hydrated user profile has no preferred language set (NULL legacy row), the system SHALL backfill the DB by persisting the currently effective locale before continuing.

#### Scenario: Hydrated profile has no preferred language

- **WHEN** `UserService.ensureLoaded()` resolves
- **AND** `UserService.current.preferredLanguage` is absent (proto `optional` field not present)
- **THEN** the system SHALL call `UserService.updatePreferredLanguage(I18N.getLocale())`
- **AND** on success, `UserService.current.preferredLanguage` SHALL match the value sent
- **AND** the active i18n locale SHALL remain unchanged (no flicker because the value matched what was already effective)

#### Scenario: Backfill RPC failure is non-fatal

- **WHEN** the backfill `UpdatePreferredLanguage` RPC fails
- **THEN** the system SHALL log a warning
- **AND** the application SHALL continue to render with the current locale
- **AND** the next hydration cycle SHALL retry the backfill (because the DB still holds NULL)

---

### Requirement: Remove Legacy localStorage Language Key After Authenticated Session Begins

Once the application has determined the user is authenticated, the system SHALL remove `localStorage['language']` so subsequent code paths cannot read a stale value. This SHALL run regardless of whether `ensureLoaded()` ultimately resolves or rejects — the legacy key must NOT survive a hydration failure, because the next boot's i18next detection chain would re-source the (now forbidden) locale from `localStorage` for an authenticated session.

#### Scenario: Cleanup runs after authenticated session begins

- **WHEN** the application determines the user is authenticated (i.e., `authService.isAuthenticated === true`)
- **THEN** the system SHALL call `localStorage.removeItem('language')` as early as possible in the authenticated lifecycle, BEFORE `ensureLoaded()` is awaited
- **AND** the removal SHALL execute even if `ensureLoaded()` subsequently fails
- **AND** the removal SHALL execute even if `preferred_language` was already populated in the hydration response

#### Scenario: Cleanup is idempotent

- **WHEN** `localStorage['language']` has already been removed
- **AND** the authenticated lifecycle runs again (e.g., subsequent boot)
- **THEN** `removeItem` SHALL be a safe no-op
- **AND** no error SHALL be raised
