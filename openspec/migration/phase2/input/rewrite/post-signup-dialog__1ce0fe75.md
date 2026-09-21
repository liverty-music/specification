<!-- spec: post-signup-dialog | target: components/infrastructure/fan/web/global/pwa-install-banner | flags: CLASSNAME | new_name: Install-prompt listener registers before routing -->

### Requirement: PwaInstallService Registers beforeinstallprompt Listener Before Routing

The `PwaInstallService` event listener for `beforeinstallprompt` SHALL be registered before any route navigation begins, so that the event is not missed during the OIDC auth-callback page load.

#### Scenario: Listener registered before auth-callback navigation

- **WHEN** the application boots and `AppShell` activates
- **THEN** `PwaInstallService` SHALL be constructed as part of `AppShell` activation
- **AND** the `beforeinstallprompt` event listener SHALL be registered before any route transition begins
- **AND** any `beforeinstallprompt` event fired during the `/auth/callback` route SHALL be captured

#### Scenario: Install row shows native button when prompt captured during auth-callback

- **WHEN** Chrome fires `beforeinstallprompt` during the `/auth/callback` page load
- **AND** the user completes sign-up and the PostSignupDialog opens on the dashboard
- **THEN** `PwaInstallService.canShowFab` SHALL be `true`
- **AND** the PostSignupDialog SHALL display the native install button in the install row
