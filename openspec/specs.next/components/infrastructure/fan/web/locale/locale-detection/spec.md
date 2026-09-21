# Locale Detection

## Purpose

Defines how the Aurelia 2 frontend renders translated strings across JA and EN locales. Covers i18n plugin registration, the detection chain that picks the initial locale, the translation-key conventions (page-keyed vs entity-keyed), how templates and TypeScript externalize strings, locale-aware date/number formatting, runtime language switching with persistence routed by authentication state, and the shared utility that lets every component switch language through one entry point.

## Requirements

### Requirement: Locale Detection
The system SHALL detect the user's preferred language using a priority chain: URL parameter, persisted preference, browser language, then fallback. Detection results SHALL be persisted to `localStorage` so that the chosen language survives subsequent reloads for anonymous users. The detection chain runs at i18next initialization, BEFORE the authenticated-user hydration cycle has resolved — its output is therefore a TENTATIVE initial locale. For authenticated sessions, the hydration cycle overrides this tentative value with the DB-sourced locale per the "Locale Sourced from Backend User Entity for Authenticated Sessions" requirement below, and the legacy `localStorage['language']` key is cleared per `user-profile-hydration`'s "Cleanup runs after authenticated session begins" scenario.

#### Scenario: URL parameter override
- **WHEN** the URL contains a `?lang=en` query parameter
- **THEN** the system SHALL set the active locale to EN regardless of other settings
- **AND** the system SHALL write `en` to `localStorage` under the `language` key

#### Scenario: Persisted preference from localStorage (tentative initial locale)
- **WHEN** no `?lang=` URL parameter is present
- **AND** localStorage contains a `language` key with value `en`
- **THEN** the system SHALL set the active locale to EN as the tentative initial value
- **AND** for an anonymous session, this tentative value SHALL be the final active locale
- **AND** for an authenticated session, this tentative value SHALL be overridden by `UserService.current.preferredLanguage` as soon as hydration resolves, AND the `localStorage['language']` key SHALL be removed per `user-profile-hydration`

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

### Requirement: Anonymous Locale is a Single Source of Truth

For an anonymous (unauthenticated) session, the active i18n locale SHALL be derived from exactly one persisted source — `localStorage['language']` (the i18next detector cache). No secondary `localStorage` key SHALL shadow, mirror, or override the anonymous locale. Any reactive projection of the anonymous locale (e.g. the value a language selector binds to for its highlight) SHALL be derived from the active i18n locale, NOT from a separate persisted key, so the selector highlight can never disagree with the rendered UI.

This requirement makes the selector's data source explicit: prior to this change the selector highlight was driven by a separate `guest.language` key that could drift from the detector's `language` key, producing a UI that rendered in one locale while the selector highlighted another.

#### Scenario: Selector highlight matches the rendered locale for an anonymous user

- **WHEN** an anonymous user opens the Settings or Welcome language selector
- **AND** the active i18n locale is `en`
- **THEN** the selector SHALL highlight the `en` option

#### Scenario: No secondary localStorage key backs the anonymous locale

- **WHEN** an anonymous user changes or has previously chosen a language
- **THEN** the only `localStorage` key that persists the anonymous locale SHALL be `language`
- **AND** the system SHALL NOT write a separate `guest.language` (or equivalent shadow) key

#### Scenario: Resetting guest state does not change the rendered locale

- **WHEN** anonymous guest state is reset (e.g. on tapping Login, before sign-in begins)
- **THEN** the guest home and per-page help-seen flags SHALL be cleared
- **AND** `localStorage['language']` SHALL be left intact
- **AND** the rendered locale SHALL NOT change as a result of the reset

---
