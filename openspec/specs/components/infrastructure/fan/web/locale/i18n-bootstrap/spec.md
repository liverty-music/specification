# I18N Bootstrap

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
