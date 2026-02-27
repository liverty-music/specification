## MODIFIED Requirements

### Requirement: About Section
The system SHALL provide access to legal and licensing information, and display the current language setting.

#### Scenario: Legal links
- **WHEN** the About section is displayed
- **THEN** the system SHALL show links to Terms of Service, Privacy Policy, and OSS Licenses
- **AND** tapping a link SHALL open the corresponding page (external or in-app webview)

## ADDED Requirements

### Requirement: Language Preference
The system SHALL allow users to change the display language of the application.

#### Scenario: Displaying language option
- **WHEN** the Settings page is displayed
- **THEN** the system SHALL show a "Language" row displaying the current language name (e.g., "日本語" or "English")

#### Scenario: Changing language
- **WHEN** a user taps the "Language" row
- **THEN** the system SHALL display a selection UI with available languages: 日本語, English
- **AND** WHEN the user selects a language
- **THEN** the system SHALL call `I18N.setLocale()` to change the active locale
- **AND** the system SHALL persist the selection in localStorage under the `language` key
- **AND** all UI text on the Settings page and throughout the app SHALL immediately update to the selected language
