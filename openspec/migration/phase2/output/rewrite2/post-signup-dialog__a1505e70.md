<!-- spec: post-signup-dialog | target: components/infrastructure/fan/web/global/post-signup-dialog | flags: CLASSNAME | new_name: Post-Signup Dialog on First Authentication -->

### Requirement: Post-Signup Dialog on First Authentication

The system SHALL display a dialog after the first successful **sign-up** that consolidates a celebration message with optional power-up actions (notification permission, PWA install), without front-loading guidance for features the user has not yet encountered.

Whether an authenticated callback is treated as a first sign-up SHALL be determined by the **flow the user initiated** — the sign-up flow versus the sign-in flow — carried as a signal that round-trips through the OIDC authorization request and back to the auth-callback. It SHALL NOT be inferred solely from the absence of a locally cached user identifier, because a returning user can arrive with an empty local cache (new browser or device, cleared storage, or a prior anonymous/guest session that never cached an identifier) and MUST NOT be treated as a new sign-up.

#### Scenario: Dialog shown after first signup

- **WHEN** the auth-callback route completes an authenticated callback whose originating flow is the **sign-up** flow
- **AND** `localStorage['liverty:postSignup:shown']` is not set
- **THEN** the system SHALL set `localStorage['liverty:postSignup:shown']` to the pending marker
- **AND** the system SHALL navigate to `/dashboard`
- **AND** the Dashboard SHALL display the post-signup dialog on load

#### Scenario: Dialog not shown on subsequent logins

- **WHEN** the auth-callback route completes for a returning user
- **AND** `localStorage['liverty:postSignup:shown']` is already set
- **THEN** the system SHALL NOT show the post-signup dialog

#### Scenario: Sign-in with an empty local cache does not trigger the dialog

- **WHEN** the auth-callback route completes an authenticated callback whose originating flow is the **sign-in** flow
- **AND** no user identifier is cached locally (e.g. a new browser/device, cleared storage, or a prior guest session)
- **THEN** the system SHALL NOT set `localStorage['liverty:postSignup:shown']` to the pending marker
- **AND** the system SHALL NOT display the celebration overlay or the post-signup dialog
- **AND** the user SHALL be navigated to `/dashboard` without a first-run payoff

#### Scenario: Dialog content leads with celebration

- **WHEN** the post-signup dialog is displayed
- **THEN** the first content row SHALL be a celebration message acknowledging completion of onboarding
- **AND** it SHALL offer a notification opt-in action if notification permission has not yet been requested
- **AND** it SHALL show a notification denied message if notification permission has been denied
- **AND** it SHALL offer a PWA install action if the app is installable and not yet installed
- **AND** it SHALL provide a dismiss/close action in the footer

#### Scenario: Footer button label when all actions are complete

- **WHEN** the post-signup dialog is displayed
- **AND** the app is not installable (already installed, or the browser lacks install support)
- **AND** notification permission has been granted
- **THEN** the footer button SHALL display the label "Close"

#### Scenario: Footer button label when actions remain

- **WHEN** the post-signup dialog is displayed
- **AND** either the app is still installable OR notification permission has not been granted
- **THEN** the footer button SHALL display the label "Later"

#### Scenario: Notification opt-in from dialog

- **WHEN** the user taps the notification opt-in button in the post-signup dialog
- **THEN** the system SHALL call `PushService.create()` (backed by `PushNotificationService.Create` RPC)
- **AND** the system SHALL NOT write any `localStorage` flag for push notification enabled state
- **AND** on success, the notification row SHALL show a confirmed state
- **AND** on failure or denial, the notification row SHALL show an error state
- **AND** the settings page SHALL subsequently derive the toggle state from the backend via `PushNotificationService.Get` without relying on any `localStorage` flag

#### Scenario: PWA install from dialog — native prompt

- **WHEN** the user taps the install button in the post-signup dialog
- **AND** the native install prompt has been captured
- **THEN** the system SHALL trigger the deferred `beforeinstallprompt` event

#### Scenario: PWA install row hidden on iOS Safari

- **WHEN** the post-signup dialog is displayed
- **AND** the browser does not support the `BeforeInstallPromptEvent` API (i.e. iOS Safari)
- **THEN** the PWA install row SHALL NOT be shown in the dialog
- **AND** the persistent `pwa-install-banner` provides the iOS install path instead

#### Scenario: Dialog dismissed

- **WHEN** the user taps the dismiss button
- **THEN** the post-signup dialog SHALL close
- **AND** the notification prompt SHALL NOT be shown again in the same session (coordinated via the prompt coordination)
- **AND** the `pwa-install-banner` SHALL become visible (it is not suppressed by post-signup dialog dismissal)
