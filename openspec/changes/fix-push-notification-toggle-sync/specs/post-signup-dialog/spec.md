## MODIFIED Requirements

### Requirement: Post-Signup Dialog on First Authentication

The system SHALL display a dialog after the first successful signup that consolidates notification permission and PWA install prompts.

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

#### Scenario: Dialog content

- **WHEN** the PostSignupDialog is displayed
- **THEN** it SHALL show a success confirmation (アカウント登録完了！)
- **AND** it SHALL always show a hype guide hint row (My Artists ページで hype を変更すると通知の範囲をコントロールできます)
- **AND** it SHALL offer a notification opt-in action (新着ライブ通知をオンにしよう) if `notificationManager.permission === 'default'`
- **AND** it SHALL show a notification denied message if `notificationManager.permission === 'denied'`
- **AND** it SHALL offer a PWA install action (ホーム画面に追加するとより快適に) if `PwaInstallService.canShowFab` is `true` AND the platform is not iOS Safari
- **AND** it SHALL provide a dismiss/close action in the footer

#### Scenario: Footer button label when all actions are complete

- **WHEN** the PostSignupDialog is displayed
- **AND** `PwaInstallService.canShowFab` is `false` (PWA already installed or not applicable)
- **AND** `notificationManager.permission` is `'granted'`
- **THEN** the footer button SHALL display the label "Close" (閉じる)

#### Scenario: Footer button label when actions remain

- **WHEN** the PostSignupDialog is displayed
- **AND** either `PwaInstallService.canShowFab` is `true` OR `notificationManager.permission` is not `'granted'`
- **THEN** the footer button SHALL display the label "Later" (あとで)

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

- **WHEN** the user taps あとで
- **THEN** the PostSignupDialog SHALL close
- **AND** the notification prompt SHALL NOT be shown again in the same session (coordinated via `IPromptCoordinator`)
- **AND** the PWA install FAB SHALL remain visible (it is not affected by PostSignupDialog dismissal)

### Requirement: PostSignupDialog footer button reflects completion state

The footer button label in PostSignupDialog SHALL dynamically reflect whether the user has completed all available actions.

#### Scenario: Button switches to "Close" after enabling notifications

- **WHEN** the user taps the notification opt-in button
- **AND** `pushService.create()` succeeds
- **AND** `canInstallPwa` is `false`
- **THEN** `notificationManager.permission` becomes `'granted'`
- **AND** `isAllDone` becomes `true`
- **AND** the footer button SHALL display "Close"
