## MODIFIED Requirements

### Requirement: Locale Detection
The system SHALL detect the user's preferred language using a priority chain: URL parameter, persisted preference, browser language, then fallback. Detection results SHALL be persisted to `localStorage` so that the chosen language survives subsequent reloads for anonymous users.

#### Scenario: URL parameter override
- **WHEN** the URL contains a `?lang=en` query parameter
- **THEN** the system SHALL set the active locale to EN regardless of other settings
- **AND** the system SHALL write `en` to `localStorage` under the `language` key

#### Scenario: Persisted preference from localStorage
- **WHEN** no `?lang=` URL parameter is present
- **AND** localStorage contains a `language` key with value `en`
- **THEN** the system SHALL set the active locale to EN

#### Scenario: Browser language detection persists to localStorage
- **WHEN** no `?lang=` URL parameter is present
- **AND** no `language` key exists in localStorage
- **AND** `navigator.language` starts with `en`
- **THEN** the system SHALL set the active locale to EN
- **AND** the system SHALL write `en` to `localStorage` under the `language` key so subsequent reloads do not re-detect

#### Scenario: Fallback to Japanese
- **WHEN** no `?lang=` URL parameter is present
- **AND** no `language` key exists in localStorage
- **AND** `navigator.language` does not match any supported locale
- **THEN** the system SHALL set the active locale to JA
- **AND** the system SHALL write `ja` to `localStorage` under the `language` key

---

### Requirement: Runtime Language Switching
The system SHALL re-render all translated strings when the active locale changes without requiring a page reload. The persistence target for the new locale SHALL depend on the authentication state: anonymous changes persist to `localStorage`; authenticated changes persist to the backend user row.

#### Scenario: Switching language mid-session as an anonymous user
- **WHEN** an unauthenticated user changes the language preference (e.g., from the Welcome page language selector)
- **THEN** all `t`-bound template strings SHALL immediately update to the new locale
- **AND** the `language` key in localStorage SHALL be updated
- **AND** the system SHALL NOT issue any backend RPC for the change
- **AND** date/number formatters SHALL use the new locale for subsequent renders

#### Scenario: Switching language mid-session as an authenticated user
- **WHEN** an authenticated user changes the language preference (e.g., from the Settings page)
- **THEN** the system SHALL call `UserService.UpdatePreferredLanguage` with the new locale
- **AND** on success, the system SHALL call `i18n.setLocale` so all `t`-bound template strings update immediately
- **AND** the system SHALL NOT read or write `localStorage['language']` for this change
- **AND** date/number formatters SHALL use the new locale for subsequent renders

#### Scenario: Authenticated language switch RPC failure
- **WHEN** the `UpdatePreferredLanguage` RPC fails (network, server error)
- **THEN** the system SHALL NOT change the active locale
- **AND** the system SHALL surface a user-visible error notification (Snack)

---

### Requirement: Shared Language Switching Utility
The system SHALL provide a shared utility for changing the active locale that selects the correct persistence path based on the caller's authentication state, so components do not duplicate this logic.

#### Scenario: Anonymous caller path
- **WHEN** any component calls the shared language-change utility while unauthenticated
- **THEN** the utility SHALL call `i18n.setLocale(lang)` and `localStorage.setItem('language', lang)`
- **AND** the utility SHALL NOT issue any backend RPC

#### Scenario: Authenticated caller path
- **WHEN** any component calls the shared language-change utility while authenticated
- **THEN** the utility SHALL call `UserService.UpdatePreferredLanguage` first
- **AND** on success, the utility SHALL call `i18n.setLocale(lang)`
- **AND** the utility SHALL NOT touch `localStorage['language']`

#### Scenario: Used by both Welcome and Settings
- **WHEN** the Welcome page (anonymous context) and Settings page (authenticated context) both change language
- **THEN** they SHALL both call the same shared utility
- **AND** the utility SHALL route persistence appropriately for each context

---

## ADDED Requirements

### Requirement: Locale Sourced from Backend User Entity for Authenticated Sessions
While the user is authenticated, the active i18n locale SHALL be sourced from `UserService.current.preferred_language` and SHALL NOT be derived from `localStorage`.

#### Scenario: i18n locale aligns with backend value on every authenticated render
- **WHEN** `UserService.current` is populated and `preferred_language` is set
- **THEN** `i18n.getLocale()` SHALL return that value
- **AND** no code path in the authenticated session SHALL read `localStorage['language']` to decide the locale

#### Scenario: localStorage language key absent during authenticated sessions
- **WHEN** the application has finished hydrating an authenticated user
- **THEN** `localStorage['language']` SHALL have been removed (handled by the hydration/auth-callback cleanup specified in `user-profile-hydration` and `user-account-sync`)
- **AND** the absence SHALL NOT affect the rendered locale, which is driven by `UserService.current.preferred_language`
