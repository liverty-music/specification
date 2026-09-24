<!-- spec: post-signup-dialog | target: components/infrastructure/fan/web/global/pwa-install-banner | flags: CLASSNAME | new_name: Install-prompt listener registers before routing -->

### Requirement: Install-prompt listener registers before routing

The install-prompt event listener for `beforeinstallprompt` SHALL be registered before any route navigation begins, so that the event is not missed during the OIDC auth-callback page load.

#### Scenario: Listener registered before auth-callback navigation

- **WHEN** the application boots and the app shell activates
- **THEN** install-prompt handling SHALL be initialized as part of app shell activation
- **AND** the `beforeinstallprompt` event listener SHALL be registered before any route transition begins
- **AND** any `beforeinstallprompt` event fired during the `/auth/callback` route SHALL be captured

#### Scenario: Install row shows native button when prompt captured during auth-callback

- **WHEN** Chrome fires `beforeinstallprompt` during the `/auth/callback` page load
- **AND** the user completes sign-up and the post-signup dialog opens on the dashboard
- **THEN** the captured install prompt SHALL be available to show
- **AND** the post-signup dialog SHALL display the native install button in the install row
