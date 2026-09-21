<!-- spec: pwa-install-banner | target: components/infrastructure/fan/web/global/pwa-install-banner | flags: CLASSNAME | new_name: Banner Disappears Permanently After Installation -->
<!-- implementation names to remove: PwaInstallService -->

### Requirement: Banner Disappears Permanently After Installation

The system SHALL remove the banner permanently once the app is installed.

#### Scenario: App installed via native dialog

- **WHEN** the browser fires the `appinstalled` event
- **THEN** `PwaInstallService.shouldShowInstallBanner` SHALL become `false`
- **AND** the banner SHALL be removed from the DOM
- **AND** the banner SHALL NOT reappear in subsequent sessions

#### Scenario: App installed confirmed manually (iOS)

- **WHEN** `PwaInstallService.confirmInstalled()` is called
- **THEN** `PwaInstallService.shouldShowInstallBanner` SHALL become `false`
- **AND** the banner SHALL be removed from the DOM
- **AND** the banner SHALL NOT reappear in subsequent sessions

---
