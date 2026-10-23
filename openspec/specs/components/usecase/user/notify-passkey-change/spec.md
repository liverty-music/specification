# components/usecase/user/notify-passkey-change Specification

## Purpose
UserUseCase.NotifyPasskeyChange emails a fan each time a passkey is added to or removed from their account, so a change made by someone else is noticed.

## Requirements

### Requirement: Each passkey change of a fan is emailed

NotifyPasskeyChange SHALL run for each announced passkey change, carrying the identity's provider user ID, the kind of change (added or removed), the passkey's name when known and the time of the change. It SHALL read the User with User.GetByProviderUserID and send the email with User.SendPasskeyChangeEmail. When no User has the provider user ID, it SHALL finish without sending, so a passkey created during sign-up is reported only when the account already exists when the change is handled. When sending fails with Unavailable, NotifyPasskeyChange SHALL fail and run again; a change announced twice can be emailed twice.

#### Scenario: Passkey added on a new device

- **WHEN** a passkey named `Google Pixel 9, Android, Chrome` is added for a fan's identity
- **THEN** the fan receives an email saying that passkey was added

#### Scenario: Passkey added through a recovery link

- **WHEN** a passkey is registered with a recovery link
- **THEN** the fan receives the same added email

#### Scenario: Passkey removed

- **WHEN** a passkey is removed from a fan's identity
- **THEN** the fan receives an email saying a passkey was removed

#### Scenario: Identity with no account

- **WHEN** the provider user ID names no User
- **THEN** no email is sent and the change is finished

#### Scenario: Mail unavailable

- **WHEN** User.SendPasskeyChangeEmail fails with Unavailable
- **THEN** NotifyPasskeyChange fails and the email is sent when it runs again
