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
