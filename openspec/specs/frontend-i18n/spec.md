## ADDED Requirements

### Requirement: i18n Plugin Registration
The system SHALL register `@aurelia/i18n` in the Aurelia 2 DI container at application startup with i18next configured for JA and EN locales.

#### Scenario: Application bootstrap with i18n
- **WHEN** the application starts
- **THEN** the system SHALL initialize `@aurelia/i18n` with i18next
- **AND** the system SHALL load JA and EN translation resources
- **AND** the fallback language SHALL be `ja`

---

### Requirement: Locale Detection
The system SHALL detect the user's preferred language using a priority chain: URL parameter, persisted preference, browser language, then fallback.

#### Scenario: URL parameter override
- **WHEN** the URL contains a `?lang=en` query parameter
- **THEN** the system SHALL set the active locale to EN regardless of other settings

#### Scenario: Persisted preference from localStorage
- **WHEN** no `?lang=` URL parameter is present
- **AND** localStorage contains a `language` key with value `en`
- **THEN** the system SHALL set the active locale to EN

#### Scenario: Browser language detection
- **WHEN** no `?lang=` URL parameter is present
- **AND** no `language` key exists in localStorage
- **AND** `navigator.language` starts with `en`
- **THEN** the system SHALL set the active locale to EN

#### Scenario: Fallback to Japanese
- **WHEN** no `?lang=` URL parameter is present
- **AND** no `language` key exists in localStorage
- **AND** `navigator.language` does not match any supported locale
- **THEN** the system SHALL set the active locale to JA

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
The system SHALL re-render all translated strings when the active locale changes without requiring a page reload.

#### Scenario: Switching language mid-session
- **WHEN** the user changes the language preference
- **THEN** all `t`-bound template strings SHALL immediately update to the new locale
- **AND** the `language` key in localStorage SHALL be updated
- **AND** date/number formatters SHALL use the new locale for subsequent renders

---

### Requirement: Shared Language Switching Utility
The system SHALL provide a shared utility function for changing the active locale, usable from any component without duplicating logic.

#### Scenario: Language switch from any component
- **WHEN** any component needs to change the active locale
- **THEN** it SHALL call a shared `changeLocale(i18n: I18N, lang: string)` function
- **AND** the function SHALL call `i18n.setLocale(lang)` and `localStorage.setItem('language', lang)`
- **AND** the Settings page and Welcome page SHALL both use this shared function
