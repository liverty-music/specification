# User.ResendVerification

## Purpose

Issues a fresh verification code for a user and sends it, whether or not an earlier code exists.

## Requirements

### Requirement: Resending issues a fresh code

ResendVerification SHALL issue a new verification code and send it to the user's registered address, even when no earlier code was ever issued. It SHALL fail with FailedPrecondition when the address is already verified, and with Internal on any other failure to issue or send.

#### Scenario: Earlier code exists

- **WHEN** ResendVerification runs for an unverified user with an earlier code
- **THEN** a new code is issued and emailed

#### Scenario: No earlier code

- **WHEN** ResendVerification runs for an unverified user who never received a code
- **THEN** a new code is issued and emailed

#### Scenario: Already verified

- **WHEN** ResendVerification runs for a user whose address is already verified
- **THEN** it fails with FailedPrecondition and nothing is sent
