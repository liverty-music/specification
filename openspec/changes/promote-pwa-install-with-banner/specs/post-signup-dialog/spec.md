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
- **AND** it SHALL offer a PWA install action if `PwaInstallService.canShowInstallOption` is `true`
- **AND** it SHALL provide a dismiss/close action in the footer

#### Scenario: Footer button label when all actions are complete

- **WHEN** the PostSignupDialog is displayed
- **AND** `PwaInstallService.canShowInstallOption` is `false` (PWA already installed or browser not capable)
- **AND** `notificationManager.permission` is `'granted'`
- **THEN** the footer button SHALL display the label "Close"

#### Scenario: Footer button label when actions remain

- **WHEN** the PostSignupDialog is displayed
- **AND** either `PwaInstallService.canShowInstallOption` is `true` OR `notificationManager.permission` is not `'granted'`
- **THEN** the footer button SHALL display the label "Later"

#### Scenario: Notification opt-in from dialog

- **WHEN** the user taps the notification opt-in button in the PostSignupDialog
- **THEN** the system SHALL call `PushService.create()` (backed by `PushNotificationService.Create` RPC)
- **AND** the system SHALL NOT write any `localStorage` flag for push notification enabled state
- **AND** on success, the notification row SHALL show a confirmed state
- **AND** on failure or denial, the notification row SHALL show an error state
- **AND** the settings page SHALL subsequently derive the toggle state from the backend via `PushNotificationService.Get` without relying on any `localStorage` flag

#### Scenario: PWA install from dialog — native prompt

- **WHEN** the user taps the install button in the PostSignupDialog
- **AND** `PwaInstallService.canShowFab` is `true` (native prompt captured)
- **THEN** the system SHALL trigger the deferred `beforeinstallprompt` event

#### Scenario: PWA install row hidden on iOS Safari

- **WHEN** the PostSignupDialog is displayed
- **AND** `PwaInstallService.browserSupportsPwa` is `false` (browser lacks `BeforeInstallPromptEvent`, i.e. iOS Safari)
- **THEN** the PWA install row SHALL NOT be shown in the dialog
- **AND** the persistent `pwa-install-banner` provides the iOS install path instead

#### Scenario: Dialog dismissed

- **WHEN** the user taps the dismiss button
- **THEN** the PostSignupDialog SHALL close
- **AND** the notification prompt SHALL NOT be shown again in the same session (coordinated via `IPromptCoordinator`)
- **AND** the `pwa-install-banner` SHALL become visible (it is not suppressed by PostSignupDialog dismissal)
