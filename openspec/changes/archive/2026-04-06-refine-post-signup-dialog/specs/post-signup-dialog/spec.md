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

## ADDED Requirements

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
- **AND** `pushService.subscribe()` succeeds
- **AND** `canInstallPwa` is `false`
- **THEN** `notificationManager.permission` becomes `'granted'`
- **AND** `isAllDone` becomes `true`
- **AND** the footer button SHALL display "Close"
