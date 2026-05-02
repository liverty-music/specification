## MODIFIED Requirements

### Requirement: Post-Signup Dialog on First Authentication

The system SHALL display a dialog after the first successful signup that consolidates a celebration message with optional power-up actions (notification permission, PWA install), without front-loading guidance for features the user has not yet encountered.

#### Scenario: Dialog shown after first signup

- **WHEN** the auth-callback route completes `provisionUser()` for a new user
- **AND** `localStorage['liverty:postSignup:shown']` is not set
- **THEN** the system SHALL set `localStorage['liverty:postSignup:shown']` to `'1'`
- **AND** the system SHALL navigate to `/dashboard`
- **AND** the Dashboard SHALL display the `PostSignupDialog` on load

#### Scenario: Dialog not shown on subsequent logins

- **WHEN** the auth-callback route completes for a returning user
- **AND** `localStorage['liverty:postSignup:shown']` is already set
- **THEN** the system SHALL NOT show the `PostSignupDialog`

#### Scenario: Dialog content leads with celebration

- **WHEN** the PostSignupDialog is displayed
- **THEN** the first content row SHALL be a celebration message acknowledging completion of onboarding
- **AND** it SHALL offer a notification opt-in action if `notificationManager.permission === 'default'`
- **AND** it SHALL show a notification denied message if `notificationManager.permission === 'denied'`
- **AND** it SHALL offer a PWA install action if `PwaInstallService.canShowFab` is `true` AND the platform is not iOS Safari
- **AND** it SHALL provide a dismiss/close action in the footer

#### Scenario: Footer button label when all actions are complete

- **WHEN** the PostSignupDialog is displayed
- **AND** `PwaInstallService.canShowFab` is `false` (PWA already installed or not applicable)
- **AND** `notificationManager.permission` is `'granted'`
- **THEN** the footer button SHALL display the label "Close"

#### Scenario: Footer button label when actions remain

- **WHEN** the PostSignupDialog is displayed
- **AND** either `PwaInstallService.canShowFab` is `true` OR `notificationManager.permission` is not `'granted'`
- **THEN** the footer button SHALL display the label "Later"

#### Scenario: Notification opt-in from dialog

- **WHEN** the user taps the notification opt-in button in the PostSignupDialog
- **THEN** the system SHALL call `PushService.create()` (backed by `PushNotificationService.Create` RPC)
- **AND** the system SHALL NOT write any `localStorage` flag for push notification enabled state
- **AND** on success, the notification row SHALL show a confirmed state
- **AND** on failure or denial, the notification row SHALL show an error state
- **AND** the settings page SHALL subsequently derive the toggle state from the backend via `PushNotificationService.Get` without relying on any `localStorage` flag

#### Scenario: PWA install from dialog (Android/Chrome)

- **WHEN** the user taps the PWA install button in the PostSignupDialog
- **AND** `beforeinstallprompt` has fired
- **THEN** the system SHALL trigger the deferred `beforeinstallprompt` event

#### Scenario: PWA install row hidden on iOS Safari

- **WHEN** the PostSignupDialog is displayed
- **AND** the platform is iOS Safari (`beforeinstallprompt` never fires)
- **THEN** the PWA install row SHALL NOT be shown in the dialog
- **AND** the persistent FAB instruction sheet provides the iOS install path instead

#### Scenario: Dialog dismissed

- **WHEN** the user taps the dismiss button
- **THEN** the PostSignupDialog SHALL close
- **AND** the notification prompt SHALL NOT be shown again in the same session (coordinated via `IPromptCoordinator`)
- **AND** the PWA install FAB SHALL remain visible (it is not affected by PostSignupDialog dismissal)

## REMOVED Requirements

### Requirement: Hype guide hint always visible in PostSignupDialog
**Reason**: The Hype guide is contextual guidance about a feature on the My Artists page; presenting it inside the post-signup celebration moment competes with the celebration tone and surfaces guidance for a screen the user has not yet visited. The `myArtists.coachMark.setHype` i18n key was never rendered by any component and was deleted in this change (see task 4.6), so Hype discoverability is accepted as a known regression — see the Discoverability trade-off note below.

**Migration**: No data migration. The `postSignup.hypeGuideLabel` i18n key (and corresponding template row) is removed from `frontend/src/locales/{ja,en}/translation.json` and the PostSignupDialog template.

**Discoverability trade-off**: removing this row reduces Hype-feature discoverability for first-time signed-up users. An i18n key `myArtists.coachMark.setHype` exists but is not currently rendered by any component, so users now discover Hype only by exploring the My Artists page on their own. If the team later judges this to be a meaningful regression, a separate change can wire a coach mark or in-page hint on the My Artists page; that is intentionally out of scope for this content-refresh change.
