# User.ResendVerification

## Purpose

Issues a fresh verification code for the User linked to a given identity at the identity provider and sends it to the registered address, whether or not an earlier code exists.

## Requirements

### Requirement: Resending issues a fresh code

ResendVerification SHALL issue a new verification code and send it to the registered address of the User with the given external id, even when no earlier code was ever issued. It SHALL fail with FailedPrecondition when the address is already verified, and with Internal on any other failure to issue or send.

#### Scenario: Earlier code exists

- **WHEN** ResendVerification runs for an unverified User with an earlier code
- **THEN** a new code is issued and emailed

#### Scenario: No earlier code

- **WHEN** ResendVerification runs for an unverified User who never received a code
- **THEN** a new code is issued and emailed

#### Scenario: Already verified

- **WHEN** ResendVerification runs for a User whose address is already verified
- **THEN** it fails with FailedPrecondition and nothing is sent

#### Scenario: Other failure

- **WHEN** the code cannot be issued or sent for any other reason
- **THEN** it fails with Internal
