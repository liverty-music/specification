# Delta for post-signup-dialog

## ADDED Requirements

### Requirement: Sign-up from the ticket sale notification button

After a sign-up that a guest started with a concert sheet's ticket sale notification button, the Timetable SHALL open that concert's detail sheet and SHALL NOT show the celebration overlay. The post-signup dialog SHALL open once the fan closes that sheet, when it has at least one step to show. Its notification step SHALL show the title 「あとはプッシュ通知をオンにするだけ！」 (EN "Just turn on push notifications!"), no body, the primary action 「通知をオンにする」 and the text action 「あとで」, and SHALL behave as the notification step does otherwise when the fan allows or blocks. The install step SHALL follow as it does otherwise.

#### Scenario: Back from sign-up
- **WHEN** a guest presses 「🔔 チケット販売の通知を受け取る」, chooses Sign Up and completes sign-up on a browser whose notification permission is undecided
- **THEN** the concert's detail sheet is open, no celebration overlay is shown and the post-signup dialog is not open

#### Scenario: Closing the sheet
- **WHEN** that fan closes the concert's detail sheet
- **THEN** the post-signup dialog opens on its notification step, titled 「あとはプッシュ通知をオンにするだけ！」 with no body

#### Scenario: Notifications already allowed
- **WHEN** the fan's notification permission was already granted and the app is installed
- **THEN** closing the concert's detail sheet opens nothing

## MODIFIED Requirements

### Requirement: Dialog title and aria-label use i18n bindings
All user-visible strings in the post-signup dialog SHALL come from the translation resources of the active locale. No display string is fixed in the markup.

#### Scenario: Title renders in Japanese locale
- **WHEN** the notification step is displayed after a sign-up started anywhere other than a concert sheet's ticket sale notification button
- **AND** the active locale is `ja`
- **THEN** the title SHALL read 「新着ライブをいち早くお知らせ」

#### Scenario: Title renders in active locale
- **WHEN** the notification step is displayed
- **AND** the active locale is `en`
- **THEN** the title SHALL be the English equivalent of the Japanese title

#### Scenario: aria-label follows active locale
- **WHEN** the post-signup dialog is displayed
- **AND** the active locale is `en`
- **THEN** the dialog's accessible name SHALL be the English text of the current step's heading

#### Scenario: Translation key parity
- **WHEN** a string of the post-signup dialog exists in the Japanese translation resource
- **THEN** the same string SHALL exist in the English translation resource

### Requirement: Celebration Precedes Post-Signup Dialog

On the post-signup Timetable redirect, the full (confetti) celebration overlay SHALL be shown before the post-signup dialog, except after a sign-up started from a concert sheet's ticket sale notification button ("Sign-up from the ticket sale notification button"). When the celebration overlay is dismissed, the post-signup dialog SHALL open if it has at least one step to show, sequencing the emotional payoff ahead of the setup actions; when it has no step to show, nothing opens after the celebration.

#### Scenario: Dialog opens after celebration dismissal

- **WHEN** a newly signed-up user is redirected to the timetable
- **AND** the full celebration overlay (per the celebration overlay "Two-Tier Celebration Overlay") is shown
- **AND** the post-signup dialog has at least one step to show
- **THEN** the system SHALL NOT display the post-signup dialog while the celebration overlay is visible
- **AND** the system SHALL display the post-signup dialog once the celebration overlay is dismissed

#### Scenario: Region selection still precedes both

- **WHEN** a newly signed-up user is redirected to the timetable
- **AND** the user has no home area yet
- **THEN** the system SHALL resolve the home-area selection first
- **AND** only then evaluate the celebration overlay, followed by the post-signup dialog on dismissal

### Requirement: Notification step says the search has started

Except after a sign-up started from a concert sheet's ticket sale notification button ("Sign-up from the ticket sale notification button"), the notification step SHALL show the title 「新着ライブをいち早くお知らせ」, the body 「フォロー中の{{count}}組のライブを探し始めました。見つかったら通知で届けます。」 where count is the number of artists the fan follows (when the fan follows none, the body is 「新しいライブが見つかったら、通知で届けます。」), the primary action 「通知をオンにする」 and the text action 「あとで」. Tapping 「通知をオンにする」 SHALL open the browser permission prompt immediately, as a direct result of the tap. When the fan allows, the fan's browser SHALL be registered for push and the dialog moves on; when the fan blocks or the registration fails, the step SHALL say so in one line, telling the fan that it can be changed later in Settings, and the dialog moves on when the fan taps 「次へ」.

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

### Requirement: Post-signup dialog asks one thing per step

The system SHALL display a dialog after the first successful **sign-up** that asks for at most one thing per step: first to turn on notifications, then to add the app to the home screen. Each step SHALL show exactly one primary action and a 「あとで」 text action that moves on. A step whose question is already answered on this device SHALL be skipped, and when no step remains the dialog SHALL NOT open.

Whether an authenticated callback is treated as a first sign-up SHALL be determined by the **flow the user initiated** — the sign-up flow versus the sign-in flow — carried as a signal that round-trips through the authorization request and back to the auth-callback. It SHALL NOT be inferred solely from the absence of a locally cached user identifier, because a returning user can arrive with an empty local cache (new browser or device, cleared storage, or a prior guest session that never cached an identifier) and MUST NOT be treated as a new sign-up.

#### Scenario: Dialog shown after first signup

- **WHEN** the auth-callback route completes an authenticated callback whose originating flow is the **sign-up** flow
- **AND** the post-signup dialog has never been scheduled on this device
- **THEN** the system SHALL schedule the post-signup celebration and dialog
- **AND** the system SHALL navigate to `/timetable`
- **AND** the Timetable SHALL show the celebration and then the dialog, except after a sign-up started from a concert sheet's ticket sale notification button, where "Sign-up from the ticket sale notification button" applies

#### Scenario: Dialog not shown on subsequent logins

- **WHEN** the auth-callback route completes for a returning user
- **AND** the post-signup dialog was already scheduled on this device
- **THEN** the system SHALL NOT show the post-signup dialog

#### Scenario: Sign-in with an empty local cache does not trigger the dialog

- **WHEN** the auth-callback route completes an authenticated callback whose originating flow is the **sign-in** flow
- **AND** no user identifier is cached locally (e.g. a new browser/device, cleared storage, or a prior guest session)
- **THEN** the system SHALL NOT schedule the post-signup celebration and dialog
- **AND** the user SHALL be navigated to `/timetable` without a first-run payoff

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
