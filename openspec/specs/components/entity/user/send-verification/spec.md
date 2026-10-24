# User.SendVerification

## Purpose

Sends a verification email to the registered address of the User linked to a given identity at the identity provider.

## Requirements

### Requirement: Sending a verification email

SendVerification SHALL send a verification email to the registered address of the User with the given provider user ID. The email SHALL be written in the User's preferred language (Japanese when none is set), SHALL be sent in the name of Liverty Music, and SHALL contain a link to the email verification screen that carries the User and a fresh code. It SHALL say that the link works for 1 hour and that the email can be ignored by someone who did not sign up. When the address is already verified it SHALL send nothing and fail with FailedPrecondition. Any other failure to send SHALL fail with Internal.

#### Scenario: Unverified user

- **WHEN** SendVerification runs for a User whose address is not verified and whose preferred language is English
- **THEN** a verification email in English is sent to that address, with a link to the email verification screen

#### Scenario: Already verified

- **WHEN** SendVerification runs for a User whose address is already verified
- **THEN** it fails with FailedPrecondition and nothing is sent

#### Scenario: Sending fails

- **WHEN** the email cannot be sent, for any reason
- **THEN** SendVerification fails with Internal
