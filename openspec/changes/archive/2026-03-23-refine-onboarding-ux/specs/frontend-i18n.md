## CHANGED Requirements

### Requirement: Shared Language Switching Utility (NEW)

The system SHALL provide a shared utility function for changing the active locale, usable from any component without duplicating logic.

#### Scenario: Language switch from any component
- **WHEN** any component needs to change the active locale
- **THEN** it SHALL call a shared `changeLocale(i18n: I18N, lang: string)` function
- **AND** the function SHALL call `i18n.setLocale(lang)` and `localStorage.setItem('language', lang)`
- **AND** the Settings page and Welcome page SHALL both use this shared function
