## MODIFIED Requirements

### Requirement: Dialog title and aria-label use i18n bindings
All user-visible strings in the post-signup dialog SHALL come from the translation resources of the active locale. No display string is fixed in the markup.

#### Scenario: Title renders in Japanese locale
- **WHEN** the notification step is displayed
- **AND** the active locale is `ja`
- **THEN** the title SHALL read 「新着ライブをいち早くお知らせ」

#### Scenario: Title renders in active locale
- **WHEN** the notification step is displayed
- **AND** the active locale is `en`
- **THEN** the title SHALL be the English equivalent of the Japanese title

#### Scenario: aria-label follows active locale
- **WHEN** the post-signup dialog is displayed
- **AND** the active locale is `en`
- **THEN** the dialog's accessible name SHALL be the English text of the dialog label

#### Scenario: Translation key parity
- **WHEN** a string of the post-signup dialog exists in the Japanese translation resource
- **THEN** the same string SHALL exist in the English translation resource

### Requirement: Celebration Precedes Post-Signup Dialog

On the post-signup Dashboard redirect, the full (confetti) celebration overlay SHALL be shown before the post-signup dialog. When the celebration overlay is dismissed, the post-signup dialog SHALL open if it has at least one step to show, sequencing the emotional payoff ahead of the setup actions; when it has no step to show, nothing opens after the celebration.

#### Scenario: Dialog opens after celebration dismissal

- **WHEN** a newly signed-up user is redirected to the dashboard
- **AND** the full celebration overlay (per the celebration overlay "Two-Tier Celebration Overlay") is shown
- **AND** the post-signup dialog has at least one step to show
- **THEN** the system SHALL NOT display the post-signup dialog while the celebration overlay is visible
- **AND** the system SHALL display the post-signup dialog once the celebration overlay is dismissed

#### Scenario: Region selection still precedes both

- **WHEN** a newly signed-up user is redirected to the dashboard
- **AND** the user has no home area yet
- **THEN** the system SHALL resolve the home-area selection first
- **AND** only then evaluate the celebration overlay, followed by the post-signup dialog on dismissal

## ADDED Requirements

### Requirement: Post-signup dialog asks one thing per step

The system SHALL display a dialog after the first successful **sign-up** that asks for at most one thing per step: first to turn on notifications, then to add the app to the home screen. Each step SHALL show exactly one primary action and a 「あとで」 text action that moves on. A step whose question is already answered on this device SHALL be skipped, and when no step remains the dialog SHALL NOT open.

Whether an authenticated callback is treated as a first sign-up SHALL be determined by the **flow the user initiated** — the sign-up flow versus the sign-in flow — carried as a signal that round-trips through the authorization request and back to the auth-callback. It SHALL NOT be inferred solely from the absence of a locally cached user identifier, because a returning user can arrive with an empty local cache (new browser or device, cleared storage, or a prior guest session that never cached an identifier) and MUST NOT be treated as a new sign-up.

#### Scenario: Dialog shown after first signup

- **WHEN** the auth-callback route completes an authenticated callback whose originating flow is the **sign-up** flow
- **AND** the post-signup dialog has never been scheduled on this device
- **THEN** the system SHALL schedule the post-signup celebration and dialog
- **AND** the system SHALL navigate to `/dashboard`
- **AND** the Dashboard SHALL show the celebration and then the dialog

#### Scenario: Dialog not shown on subsequent logins

- **WHEN** the auth-callback route completes for a returning user
- **AND** the post-signup dialog was already scheduled on this device
- **THEN** the system SHALL NOT show the post-signup dialog

#### Scenario: Sign-in with an empty local cache does not trigger the dialog

- **WHEN** the auth-callback route completes an authenticated callback whose originating flow is the **sign-in** flow
- **AND** no user identifier is cached locally (e.g. a new browser/device, cleared storage, or a prior guest session)
- **THEN** the system SHALL NOT schedule the post-signup celebration and dialog
- **AND** the user SHALL be navigated to `/dashboard` without a first-run payoff

#### Scenario: Both steps in order

- **WHEN** the dialog opens on a browser where notification permission is not yet decided and the app can be installed but is not installed
- **THEN** the dialog SHALL first show the notification step
- **AND** after the fan taps 「通知をオンにする」 or 「あとで」, the dialog SHALL show the install step
- **AND** after the fan taps 「ホーム画面に置く」 or 「あとで」 on the install step, the dialog SHALL close

#### Scenario: Notification already decided

- **WHEN** the dialog opens and notification permission is already granted or blocked
- **THEN** the notification step SHALL be skipped

#### Scenario: Nothing left to ask

- **WHEN** notification permission is already decided and the app is installed or cannot be installed
- **THEN** the dialog SHALL NOT open after the celebration

### Requirement: Notification step says the search has started

The notification step SHALL show the title 「新着ライブをいち早くお知らせ」, the body 「フォロー中の{{count}}組のライブを探し始めました。見つかったら通知で届けます。」 where count is the number of artists the fan follows (when the fan follows none, the body is 「新しいライブが見つかったら、通知で届けます。」), the primary action 「通知をオンにする」 and the text action 「あとで」. Tapping 「通知をオンにする」 SHALL open the browser permission prompt immediately, as a direct result of the tap. When the fan allows, the fan's browser SHALL be registered for push and the dialog moves on; when the fan blocks or the registration fails, the step SHALL say so in one line, telling the fan that it can be changed later in Settings, and the dialog moves on when the fan taps 「次へ」.

#### Scenario: Fan follows five artists

- **WHEN** the notification step opens for a fan who follows 5 artists
- **THEN** the body SHALL read 「フォロー中の5組のライブを探し始めました。見つかったら通知で届けます。」

#### Scenario: Fan follows no artist

- **WHEN** the notification step opens for a fan who follows no artist
- **THEN** the body SHALL read 「新しいライブが見つかったら、通知で届けます。」

#### Scenario: Fan allows notifications

- **WHEN** the fan taps 「通知をオンにする」 and allows in the browser prompt
- **THEN** the fan's browser SHALL be registered for push
- **AND** the Settings notification toggle SHALL show on afterwards
- **AND** the dialog SHALL move to the next step, or close when none remains

#### Scenario: Fan blocks notifications

- **WHEN** the fan taps 「通知をオンにする」 and blocks in the browser prompt
- **THEN** the step SHALL show one line saying notifications are blocked and can be changed later in Settings
- **AND** tapping 「次へ」 SHALL move to the next step, or close the dialog when none remains

### Requirement: Install step asks for one thing

The install step SHALL be shown only when the browser can install the app and the app is not installed. It SHALL say what the fan gains, not name the task: the app icon, the title 「ワンタップでタイムテーブルへ」, the body 「ホーム画面に置いておけば、アプリのようにすぐ開けます。」, the primary action 「ホーム画面に置く」 and the text action 「あとで」. When the browser offers its own install prompt, 「ホーム画面に置く」 SHALL open it; otherwise 「ホーム画面に置く」 SHALL reveal 3 numbered steps for adding the app from the browser menu: open the browser menu (⋮), choose 「ホーム画面に追加」, tap 「追加」. If the browser's own install prompt becomes available while the step is open, 「ホーム画面に置く」 SHALL open it from then on.

#### Scenario: Browser offers an install prompt

- **WHEN** the install step is shown and the browser offers its own install prompt
- **AND** the fan taps 「ホーム画面に置く」
- **THEN** the browser's install prompt SHALL open
- **AND** the dialog SHALL close after the prompt is answered

#### Scenario: No install prompt available

- **WHEN** the install step is shown and the browser offers no install prompt
- **AND** the fan taps 「ホーム画面に置く」
- **THEN** the 3 numbered menu steps SHALL appear in the step

#### Scenario: App already installed

- **WHEN** the dialog runs and the app is already installed
- **THEN** the install step SHALL NOT be shown

### Requirement: iOS and iPadOS show the add-to-home-screen steps instead

On iOS and iPadOS when the app is not installed, the dialog SHALL show a single step instead of both steps, because notifications there work only for an app added to the home screen. The step SHALL show the title 「新着ライブをいち早くお知らせ」, the body 「iPhone では、ホーム画面に追加すると通知を受け取れます。」, 3 numbered steps (tap the share button, choose 「ホーム画面に追加」, open the app from the new icon) and the text action 「あとで」. It SHALL NOT show a 「通知をオンにする」 action.

#### Scenario: iPhone without the app installed

- **WHEN** the dialog opens on an iPhone in Safari and the app is not on the home screen
- **THEN** the dialog SHALL show the title, the body and the 3 numbered steps
- **AND** no 「通知をオンにする」 action SHALL be shown

#### Scenario: iPhone with the app installed

- **WHEN** the dialog opens in the app launched from the iPhone home screen
- **THEN** the dialog SHALL show the notification step as on other platforms

## REMOVED Requirements

### Requirement: Dialog footer button reflects completion state

**Reason**: Each step now has its own primary action and a 「あとで」 text action; there is no shared footer whose label changes.
**Migration**: See "Post-Signup Dialog on First Authentication" and the step requirements.

### Requirement: PWA Install Row Shows Fallback Instructions When Native Prompt Unavailable

**Reason**: The install row is replaced by the install step.
**Migration**: The manual menu steps and the switch to the browser's prompt are in "Install step asks for one thing".

### Requirement: Post-Signup Dialog on First Authentication

**Reason**: The single dialog with a celebration row, a notification row, an install row and a shared footer is replaced by steps that each ask one thing.
**Migration**: See "Post-signup dialog asks one thing per step"; the first-sign-up detection is unchanged and moves there.
