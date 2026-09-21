<!-- spec: pwa-install-banner | target: components/infrastructure/fan/web/global/pwa-install-banner | flags: CLASSNAME | new_name: Banner visibility state and installed confirmation -->

### Requirement: Banner visibility state and installed confirmation

The system SHALL expose a reactive property and a method to support the install banner's lifecycle.

#### Scenario: Install banner shown for Chrome/Edge non-installed users

- **WHEN** the browser supports PWA installation
- **AND** the app has not been installed
- **THEN** the install banner SHALL be shown

#### Scenario: Install banner shown for iOS non-installed users

- **WHEN** the browser is iOS
- **AND** the app has not been installed
- **THEN** the install banner SHALL be shown

#### Scenario: Install banner hides on appinstalled

- **WHEN** the browser fires the `appinstalled` event
- **THEN** the install banner SHALL reactively hide

#### Scenario: Confirming installation marks the app as installed

- **WHEN** the installed-confirmation action is invoked
- **THEN** the system SHALL persist that the app has been installed
- **AND** the install banner SHALL hide
