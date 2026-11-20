# Spec Delta

## MODIFIED Requirements

### Requirement: Post-signup dialog asks one thing per step

The system SHALL display a dialog after the first successful **sign-up** that asks for at most one thing per step: first to turn on notifications, then to add the app to the home screen. Each step SHALL show exactly one primary action and a 「あとで」 text action that moves on. A step whose question is already answered on this device SHALL be skipped, and when no step remains the dialog SHALL NOT open.

Whether an authenticated callback is treated as a first sign-up SHALL be determined by the **flow the user initiated** — the sign-up flow versus the sign-in flow — carried as a signal that round-trips through the authorization request and back to the auth-callback. It SHALL NOT be inferred solely from the absence of a locally cached user identifier, because a returning user can arrive with an empty local cache (new browser or device, cleared storage, or a prior guest session that never cached an identifier) and MUST NOT be treated as a new sign-up.

#### Scenario: Dialog shown after first signup

- **WHEN** the auth-callback route completes an authenticated callback whose originating flow is the **sign-up** flow
- **AND** the post-signup dialog has never been scheduled on this device
- **THEN** the system SHALL schedule the post-signup celebration and dialog
- **AND** the system SHALL navigate to `/timetable`
- **AND** the Timetable SHALL show the celebration and then the dialog

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
