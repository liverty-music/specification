# Date Number Formatting

## Purpose

Defines how the Aurelia 2 frontend renders translated strings across JA and EN locales. Covers i18n plugin registration, the detection chain that picks the initial locale, the translation-key conventions (page-keyed vs entity-keyed), how templates and TypeScript externalize strings, locale-aware date/number formatting, runtime language switching with persistence routed by authentication state, and the shared utility that lets every component switch language through one entry point.

## Requirements

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
