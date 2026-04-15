# Post-Signup Dialog

## Purpose

Consolidates notification permission and PWA install prompts into a single dialog shown after the first successful signup, providing a streamlined post-authentication experience.

## Requirements

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

### Requirement: Dialog reliably opens when active is true at creation time
The PostSignupDialog SHALL reliably open when `active` is bound to `true` at component creation time, not only when `active` transitions from `false` to `true` after the component is attached.

#### Scenario: Dashboard sets showPostSignupDialog in loading() before attach
- **WHEN** `DashboardRoute.loading()` sets `showPostSignupDialog = true`
- **AND** `PostSignupDialog` receives `active = true` during its `binding` phase
- **THEN** `activeChanged()` SHALL set `isOpen = true`
- **AND** the inner `<bottom-sheet>` SHALL open successfully (via the `attached()` fallback in BottomSheet)
- **AND** the dialog SHALL be visible to the user with its full content

### Requirement: PostSignupDialog title and aria-label use i18n bindings
All user-visible strings in the PostSignupDialog component SHALL use `@aurelia/i18n` `t` attribute bindings. No hardcoded display strings are permitted in the template.

#### Scenario: Title renders in active locale
- **WHEN** the PostSignupDialog is displayed
- **AND** the active locale is `en`
- **THEN** the `<h2>` title SHALL render using the `postSignup.title` translation key in the EN translation
- **AND** the rendered text SHALL be in English (e.g., `Account registration complete!`)

#### Scenario: Title renders in Japanese locale
- **WHEN** the PostSignupDialog is displayed
- **AND** the active locale is `ja`
- **THEN** the `<h2>` title SHALL render using the `postSignup.title` translation key in the JA translation
- **AND** the rendered text SHALL be `✅ アカウント登録完了！`

#### Scenario: aria-label follows active locale
- **WHEN** the PostSignupDialog is displayed
- **AND** the active locale is `en`
- **THEN** the wrapping `<bottom-sheet>` element SHALL have an `aria-label` rendered from the `postSignup.ariaLabel` translation key in the EN translation

#### Scenario: Translation key parity
- **WHEN** `postSignup.title` or `postSignup.ariaLabel` keys exist in `ja/translation.json`
- **THEN** the same keys SHALL exist in `en/translation.json`

### Requirement: Hype guide hint always visible in PostSignupDialog

The PostSignupDialog SHALL always display a hype guide hint row, regardless of notification permission state or PWA installation state.

#### Scenario: Hype guide row shown when PWA installed and notification granted

- **WHEN** the PostSignupDialog is displayed
- **AND** PWA is already installed
- **AND** `notificationManager.permission` is `'granted'`
- **THEN** the hype guide hint row SHALL still be visible
- **AND** the footer button SHALL display "Close"

#### Scenario: Hype guide row shown when no actions are available

- **WHEN** the PostSignupDialog is displayed
- **AND** no notification row and no PWA install row are shown
- **THEN** the hype guide hint row SHALL remain visible
- **AND** the dialog SHALL NOT appear empty

### Requirement: PostSignupDialog footer button reflects completion state

The footer button label in PostSignupDialog SHALL dynamically reflect whether the user has completed all available actions.

#### Scenario: Button switches to "Close" after enabling notifications

- **WHEN** the user taps the notification opt-in button
- **AND** `pushService.create()` succeeds
- **AND** `canInstallPwa` is `false`
- **THEN** `notificationManager.permission` becomes `'granted'`
- **AND** `isAllDone` becomes `true`
- **AND** the footer button SHALL display "Close"
