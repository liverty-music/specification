## Purpose

Emails a User that a passkey was added to or removed from their account, so a change they did not make is noticed.

## ADDED Requirements

### Requirement: SendPasskeyChangeEmail tells the user what changed

SendPasskeyChangeEmail SHALL take the User, the kind of change (added or removed) and the passkey's name, and SHALL send one email to the User's email address in the User's preferred language (Japanese when none). The email SHALL state the kind of change, the passkey's name when it is not empty, and the time of the change in Japan time, and SHALL tell the reader to open the "can't sign in" screen and remove unknown passkeys in Settings when they did not make the change. It SHALL fail with InvalidArgument when the User has no email address and with Unavailable when email cannot be sent.

#### Scenario: Passkey added

- **WHEN** SendPasskeyChangeEmail runs for a User with preferred language `ja`, kind added and the name `Apple iPhone, iOS, Mobile Safari`
- **THEN** one Japanese email reaches the User saying a passkey named `Apple iPhone, iOS, Mobile Safari` was added, when, and what to do if they did not add it

#### Scenario: Passkey removed

- **WHEN** SendPasskeyChangeEmail runs with kind removed and an empty name
- **THEN** one email reaches the User saying a passkey was removed, without a name

#### Scenario: Mail unavailable

- **WHEN** email cannot be sent
- **THEN** SendPasskeyChangeEmail fails with Unavailable
