## ADDED Requirements

### Requirement: Welcome Page Language Switcher

The landing page SHALL provide a language toggle for unauthenticated users to switch between supported locales without requiring sign-in.

#### Scenario: Language toggle visible on welcome page
- **WHEN** an unauthenticated user visits the welcome page
- **THEN** the system SHALL display a language toggle below the Log In button
- **AND** the toggle SHALL show all supported languages (EN, JA)
- **AND** the current active language SHALL be visually distinguished (e.g., bold or underline)

#### Scenario: Switching language on welcome page
- **WHEN** the user taps a language option
- **THEN** the system SHALL call `i18n.setLocale(lang)` to update all translated strings immediately
- **AND** the system SHALL persist the choice via `localStorage.setItem('language', lang)`
- **AND** no page reload SHALL be required

#### Scenario: Language preference persists across sessions
- **WHEN** the user selects a language on the welcome page and later returns
- **THEN** the i18next language detector SHALL read the persisted `language` key from localStorage
- **AND** the application SHALL start in the previously selected language
