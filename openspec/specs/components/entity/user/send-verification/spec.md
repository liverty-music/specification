# User.SendVerification

## Purpose

Sends a verification email to the registered address of the User linked to a given identity at the identity provider.

## Requirements

### Requirement: Sending a verification email

SendVerification SHALL send a verification email to the registered address of the User with the given external id. Any failure to send SHALL fail with Internal.

#### Scenario: Unverified user

- **WHEN** SendVerification runs for a User whose address is not verified
- **THEN** a verification email is sent to that address

#### Scenario: Sending fails

- **WHEN** the email cannot be sent, for any reason
- **THEN** SendVerification fails with Internal
