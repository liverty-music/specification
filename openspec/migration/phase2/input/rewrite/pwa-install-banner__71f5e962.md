<!-- spec: pwa-install-banner | target: components/infrastructure/fan/web/global/pwa-install-banner | flags: CLASSNAME | new_name: Banner visibility state and installed confirmation -->

### Requirement: PwaInstallService Banner Visibility API

`PwaInstallService` SHALL expose a reactive property and a method to support the banner's lifecycle.

#### Scenario: shouldShowInstallBanner is true for Chrome/Edge non-installed users

- **WHEN** `PwaInstallService.browserSupportsPwa` is `true`
- **AND** the app has not been installed
- **THEN** `PwaInstallService.shouldShowInstallBanner` SHALL be `true`

#### Scenario: shouldShowInstallBanner is true for iOS non-installed users

- **WHEN** `PwaInstallService.isIos` is `true`
- **AND** the app has not been installed
- **THEN** `PwaInstallService.shouldShowInstallBanner` SHALL be `true`

#### Scenario: shouldShowInstallBanner becomes false on appinstalled

- **WHEN** the browser fires the `appinstalled` event
- **THEN** `PwaInstallService.shouldShowInstallBanner` SHALL reactively update to `false`

#### Scenario: confirmInstalled marks the app as installed

- **WHEN** `PwaInstallService.confirmInstalled()` is called
- **THEN** the service SHALL persist `localStorage['pwa.installed'] = 'true'`
- **AND** `PwaInstallService.shouldShowInstallBanner` SHALL become `false`
