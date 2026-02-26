## ADDED Requirements

### Requirement: PWA Install Prompt
The system SHALL capture the browser's `beforeinstallprompt` event and display a custom install banner to encourage users to add the app to their home screen.

#### Scenario: First session — no prompt shown
- **WHEN** a user visits the application for the first time
- **THEN** the system SHALL increment the session count in `localStorage` (`liverty-music:session-count`)
- **AND** the system SHALL NOT display the install banner

#### Scenario: Second session — install banner displayed
- **WHEN** a user visits the application and the session count is 2 or greater
- **AND** the user has not previously dismissed the install banner
- **AND** the browser has fired the `beforeinstallprompt` event
- **THEN** the system SHALL display a non-intrusive install banner within the app shell's main content area
- **AND** the banner SHALL include a message communicating the benefit of installation (e.g., "Add to Home Screen for faster access")
- **AND** the banner SHALL include an "Install" action button and a "Not now" dismiss button

#### Scenario: User taps Install
- **WHEN** the user taps the "Install" button on the install banner
- **THEN** the system SHALL trigger the deferred `beforeinstallprompt` event's `prompt()` method
- **AND** the system SHALL hide the install banner regardless of the user's choice in the native dialog

#### Scenario: User dismisses the banner
- **WHEN** the user taps "Not now" on the install banner
- **THEN** the system SHALL hide the install banner
- **AND** the system SHALL persist the dismissal in `localStorage` (`liverty-music:install-prompt-dismissed`)
- **AND** the system SHALL NOT show the install banner again in future sessions

#### Scenario: Browser does not support install prompt
- **WHEN** the browser does not fire the `beforeinstallprompt` event (e.g., Safari, Firefox, or app is already installed)
- **THEN** the system SHALL NOT display the install banner
- **AND** the system SHALL NOT produce any error or console warning
