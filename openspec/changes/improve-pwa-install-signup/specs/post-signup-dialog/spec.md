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
- **AND** the persistent FAB instruction sheet provides the iOS install path instead

#### Scenario: Dialog dismissed

- **WHEN** the user taps the dismiss button
- **THEN** the PostSignupDialog SHALL close
- **AND** the notification prompt SHALL NOT be shown again in the same session (coordinated via `IPromptCoordinator`)
- **AND** the PWA install FAB SHALL remain visible (it is not affected by PostSignupDialog dismissal)

## ADDED Requirements

### Requirement: PWA Install Row Shows Fallback Instructions When Native Prompt Unavailable

When the browser supports PWA install but the native prompt has not been captured, the PostSignupDialog SHALL show a manual install guide rather than hiding the row.

#### Scenario: Install row shows "How to add" button when deferredPrompt is absent

- **WHEN** the PostSignupDialog is displayed
- **AND** `PwaInstallService.canShowInstallOption` is `true` (browser supports PWA install)
- **AND** `PwaInstallService.canShowFab` is `false` (native prompt not yet captured)
- **THEN** the install row SHALL display a "How to add" button instead of the native install button

#### Scenario: Tapping "How to add" reveals inline instructions

- **WHEN** the user taps the "How to add" button in the install row
- **THEN** the install row SHALL expand to show numbered steps for browser-menu-based installation:
  1. Open the browser menu (⋮)
  2. Select "Add to Home Screen"
  3. Tap "Add" to finish
- **AND** the "How to add" button SHALL be replaced by the expanded steps

#### Scenario: Install row reactively upgrades to native button on prompt arrival

- **WHEN** the PostSignupDialog is open
- **AND** the browser fires `beforeinstallprompt` (native prompt arrives after dialog opened)
- **THEN** `PwaInstallService.canShowFab` becomes `true`
- **AND** the install row SHALL update reactively to show the native install button
- **AND** the fallback instruction content SHALL be replaced by the native install button

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
