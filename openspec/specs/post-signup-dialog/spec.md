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
- **AND** it SHALL offer a notification opt-in action (新着ライブ通知をオンにしよう)
- **AND** it SHALL offer a PWA install action (ホーム画面に追加するとより快適に)
- **AND** it SHALL provide a dismiss action (あとで)

#### Scenario: Notification opt-in from dialog

- **WHEN** the user taps the notification opt-in button in the PostSignupDialog
- **THEN** the system SHALL call `PushService.subscribe()`
- **AND** on success, the notification row SHALL show a confirmed state
- **AND** on failure or denial, the notification row SHALL show an error state

#### Scenario: PWA install from dialog

- **WHEN** the user taps the PWA install button in the PostSignupDialog
- **THEN** the system SHALL trigger the deferred `beforeinstallprompt` event
- **AND** if the event is not available (already installed or not supported), the button SHALL be hidden

#### Scenario: Dialog dismissed

- **WHEN** the user taps あとで
- **THEN** the PostSignupDialog SHALL close
- **AND** neither prompt SHALL be shown again in the same session (coordinated via `IPromptCoordinator`)
