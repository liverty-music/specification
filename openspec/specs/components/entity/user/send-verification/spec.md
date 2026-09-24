# User.SendVerification

## Purpose

Sends a verification email to a user's registered address.

## Requirements

### Requirement: Sending a verification email

SendVerification SHALL send a verification email to the user's registered address. Sending it again for the same user SHALL have no adverse effect. Any failure to send SHALL fail with Internal.

#### Scenario: Unverified user

- **WHEN** SendVerification runs for a user whose address is not verified
- **THEN** a verification email is sent to that address

#### Scenario: Sent twice

- **WHEN** SendVerification runs twice for the same user
- **THEN** the user may receive a second email and nothing else changes

#### Scenario: Sending fails

- **WHEN** the email cannot be sent
- **THEN** SendVerification fails with Internal
