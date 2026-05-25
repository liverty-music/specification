# Frontend i18n

## Purpose

Defines how the Aurelia 2 frontend renders translated strings across JA and EN locales. Covers i18n plugin registration, the detection chain that picks the initial locale, the translation-key conventions (page-keyed vs entity-keyed), how templates and TypeScript externalize strings, locale-aware date/number formatting, runtime language switching with persistence routed by authentication state, and the shared utility that lets every component switch language through one entry point.

## Requirements

### Requirement: i18n Plugin Registration
The system SHALL register `@aurelia/i18n` in the Aurelia 2 DI container at application startup with i18next configured for JA and EN locales.

#### Scenario: Application bootstrap with i18n
- **WHEN** the application starts
- **THEN** the system SHALL initialize `@aurelia/i18n` with i18next
- **AND** the system SHALL load JA and EN translation resources
- **AND** the fallback language SHALL be `ja`

---

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

### Requirement: Translation Resource Files
The system SHALL maintain translation JSON files for each supported locale with identical key structures.

#### Scenario: Key parity between locales
- **WHEN** a translation key exists in `ja/translation.json`
- **THEN** the same key SHALL exist in `en/translation.json`
- **AND** missing keys in EN SHALL fall back to the JA value

#### Scenario: Page-keyed naming convention
- **WHEN** a new translation key is added under any top-level namespace other than `entity`
- **THEN** the key SHALL follow the pattern `<page>.<component>.<element>` (e.g., `welcome.hero.title`, `settings.language.label`)

#### Scenario: Entity-keyed naming convention
- **WHEN** a new translation key is added under the `entity` top-level namespace
- **THEN** the key SHALL follow the pattern `entity.<entityStem>.label` for an entity's display name
- **AND** enum value labels SHALL follow the pattern `entity.<entityStem>.values.<lowerCamelValue>`
- **AND** `<entityStem>` SHALL be derived from the protobuf entity name per the `brand-vocabulary` capability's mirroring rule

#### Scenario: Reserved top-level namespace
- **WHEN** a developer adds a top-level key named `entity`
- **THEN** the key SHALL be reserved exclusively for entity-grounded labels managed by the `brand-vocabulary` capability
- **AND** ad-hoc page-keyed strings SHALL NOT be placed under `entity.*`

---

### Requirement: Template String Externalization
The system SHALL replace all hardcoded Japanese strings in Aurelia 2 HTML templates with `t` attribute bindings that reference translation keys.

#### Scenario: Static text in templates
- **WHEN** a template contains a hardcoded display string (e.g., headings, labels, button text)
- **THEN** the string SHALL be replaced with a `t` attribute binding (e.g., `<h1 t="welcome.hero.title"></h1>`)
- **AND** the corresponding translation keys SHALL exist in both JA and EN resource files

#### Scenario: Dynamic text with interpolation
- **WHEN** a template contains a string with dynamic values (e.g., a count or name)
- **THEN** the string SHALL use i18next interpolation syntax (e.g., `t="key;count.bind:count"`)

---

### Requirement: TypeScript String Externalization
The system SHALL replace all hardcoded Japanese strings in TypeScript files (error messages, toast notifications, loading text) with `I18N.tr()` calls.

#### Scenario: Error and toast messages
- **WHEN** a TypeScript file contains a hardcoded Japanese string used for user-facing messages
- **THEN** the string SHALL be replaced with `this.i18n.tr('key')` using the injected `I18N` service

---

### Requirement: Locale-Aware Date and Number Formatting
The system SHALL format dates and numbers according to the active locale instead of hardcoding `ja-JP`.

#### Scenario: Date formatting follows active locale
- **WHEN** a date is displayed using the date ValueConverter
- **THEN** the system SHALL use `@aurelia/i18n`'s `df` ValueConverter or `Intl.DateTimeFormat` with the active i18next language
- **AND** JA locale SHALL display dates in Japanese format (e.g., `3月15日`)
- **AND** EN locale SHALL display dates in English format (e.g., `Mar 15`)

#### Scenario: Relative time formatting follows active locale
- **WHEN** a relative time is displayed (e.g., "3 days ago")
- **THEN** the system SHALL use `Intl.RelativeTimeFormat` with the active i18next language

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
- **THEN** the active locale SHALL end at the value it held before the change was attempted (the implementation MAY apply the new locale optimistically and revert on failure; the user-observable end-state SHALL be unchanged)
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

### Requirement: Legacy Key Removal After Entity Migration

When a top-level i18n namespace is superseded by an `entity.*` namespace path, the legacy keys SHALL be removed from both `ja/translation.json` and `en/translation.json` in the same change that introduces the `entity.*` replacements.

#### Scenario: hype.* migrated to entity.hype.*

- **WHEN** `entity.hype.label` and `entity.hype.values.{watch,home,nearby,away}` are populated in both locales
- **AND** all template / TypeScript bindings are switched to read from `entity.hype.*`
- **THEN** the legacy `hype.watch`, `hype.home`, `hype.nearby`, `hype.away` keys SHALL be removed from both locale files
- **AND** no source file SHALL retain a reference to a removed legacy key (verified by Biome / typecheck against generated i18n key types if available, otherwise by grep in CI)

#### Scenario: Per-screen hype labels collapse into the entity path

- **WHEN** a screen-local key (e.g. `myArtists.table.watch`, `myArtists.hypeExplanation.watch`, `myArtists.table.home`) duplicates a value now expressible via `entity.hype.values.*` or `entity.hype.label`
- **THEN** the screen template SHALL bind to the `entity.*` path instead
- **AND** the duplicate screen-local key SHALL be removed from both locale files
- **AND** any wording variation in the screen-local key (e.g. `近郊まで` vs `近郊`, `どこでも！` vs `全国`) SHALL be reconciled in favor of the canonical `entity.hype.values.*` value, eliminating the variant
