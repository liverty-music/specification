<!-- spec: pwa-install-banner | target: components/infrastructure/fan/web/global/pwa-install-banner | flags: CLASSNAME | new_name: Banner Disappears Permanently After Installation -->

### Requirement: Banner Disappears Permanently After Installation

The system SHALL remove the banner permanently once the app is installed.

#### Scenario: App installed via native dialog

- **WHEN** the browser fires the `appinstalled` event
- **THEN** the system SHALL determine the banner should no longer be shown
- **AND** the banner SHALL be removed from the DOM
- **AND** the banner SHALL NOT reappear in subsequent sessions

#### Scenario: App installed confirmed manually (iOS)

- **WHEN** the user confirms manual installation
- **THEN** the system SHALL determine the banner should no longer be shown
- **AND** the banner SHALL be removed from the DOM
- **AND** the banner SHALL NOT reappear in subsequent sessions
