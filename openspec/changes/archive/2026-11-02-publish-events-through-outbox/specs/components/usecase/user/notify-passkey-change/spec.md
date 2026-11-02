## MODIFIED Requirements

### Requirement: Each passkey change of a fan is emailed

NotifyPasskeyChange SHALL run for each Passkey announced as added by Passkey.Create or as removed by Passkey.Delete, carrying the Passkey. It SHALL read the Passkey's User with User.Get and send the email with User.SendPasskeyChangeEmail, with the kind of change, the Passkey's name (empty when it has none), and as the time of the change the Passkey's create time for an added Passkey and the time the removal was announced for a removed one. When User.Get fails with NotFound, it SHALL finish without sending. Because a Passkey is recorded only once its User exists, the passkey registered at sign-up is emailed as added once it is recorded. When sending fails with Unavailable, NotifyPasskeyChange SHALL fail and run again; an announcement delivered twice is emailed once.

#### Scenario: Passkey added on a new device

- **WHEN** a Passkey named `Google Pixel 9, Android, Chrome` is announced as added for a fan
- **THEN** the fan receives an email saying that passkey was added

#### Scenario: Passkey added through a recovery link

- **WHEN** a passkey registered with a recovery link is recorded and announced as added
- **THEN** the fan receives the same added email

#### Scenario: Passkey registered at sign-up

- **WHEN** the passkey a fan registered at sign-up is recorded after the fan's User was created, and announced as added
- **THEN** the fan receives the added email

#### Scenario: Passkey removed

- **WHEN** a fan's Passkey is announced as removed
- **THEN** the fan receives an email saying a passkey was removed

#### Scenario: Identity with no account

- **WHEN** the Passkey's User no longer exists, so User.Get fails with NotFound
- **THEN** no email is sent and the change is finished

#### Scenario: Delivered twice

- **WHEN** the same added Passkey announcement is delivered twice
- **THEN** the fan receives one email

#### Scenario: Mail unavailable

- **WHEN** User.SendPasskeyChangeEmail fails with Unavailable
- **THEN** NotifyPasskeyChange fails and the email is sent when it runs again
