# Language Switching

## Purpose

Defines how the Aurelia 2 frontend renders translated strings across JA and EN locales. Covers i18n plugin registration, the detection chain that picks the initial locale, the translation-key conventions (page-keyed vs entity-keyed), how templates and TypeScript externalize strings, locale-aware date/number formatting, runtime language switching with persistence routed by authentication state, and the shared utility that lets every component switch language through one entry point.

## Requirements

### Requirement: Language Switching

The system SHALL re-render all translated strings when the active locale
changes without requiring a page reload, using a shared utility for changing
the active locale that selects the correct persistence path based on the
caller's authentication state, so components do not duplicate this logic.
The persistence target SHALL depend on the authentication state: anonymous
changes persist to `localStorage`; authenticated changes persist to the
backend user row via `UserService.UpdatePreferredLanguage`.

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
- **THEN** the active locale SHALL end at the value it held before the change was attempted (the implementation MAY apply the new locale optimistically and revert on failure; the user-observable end-state SHALL be unchanged)
- **AND** the system SHALL surface a user-visible error notification (Snack)

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

---
