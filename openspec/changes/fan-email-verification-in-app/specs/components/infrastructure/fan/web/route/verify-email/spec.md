## Purpose

The screen a verification email's link opens: it lets the fan confirm their address with one tap, without signing in, and tells them what happened and where to go next.

## ADDED Requirements

### Requirement: The address is confirmed only on the fan's tap

The email verification screen SHALL open without sign-in and SHALL NOT confirm the address on opening. It SHALL show a "メールアドレスを確認する" action, and only that action SHALL call UserUseCase.VerifyEmail with the User and code from the link. While the call runs, the action SHALL be disabled.

#### Scenario: Opening the link

- **WHEN** the fan, or a mail scanner, opens the link
- **THEN** the screen shows the confirm action and nothing is verified

#### Scenario: Fan confirms

- **WHEN** the fan taps "メールアドレスを確認する"
- **THEN** UserUseCase.VerifyEmail runs for the link's User and code

### Requirement: The screen shows the outcome and the next step

After a successful confirmation the screen SHALL say the address is verified and SHALL offer to open the app. When the confirmation fails with InvalidArgument, it SHALL say the link has expired or was already used, and that a new email can be sent from Settings. For ResourceExhausted it SHALL say to try again later. For Unavailable or a network failure it SHALL say so and offer to try again. A link without a User or a code SHALL show the expired-or-used message without calling anything.

#### Scenario: Verified

- **WHEN** the confirmation succeeds
- **THEN** the screen says the address is verified and offers to open the app

#### Scenario: Expired or used link

- **WHEN** the confirmation fails with InvalidArgument
- **THEN** the screen says the link has expired or was already used and that a new email can be sent from Settings

#### Scenario: Too many attempts

- **WHEN** the confirmation fails with ResourceExhausted
- **THEN** the screen says to try again later

#### Scenario: Network failure

- **WHEN** the confirmation cannot reach the server
- **THEN** the screen says so and offers to try again

#### Scenario: Broken link

- **WHEN** the link has no code
- **THEN** the screen shows the expired-or-used message and calls nothing
