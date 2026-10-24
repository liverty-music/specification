## MODIFIED Requirements

### Requirement: Resending issues a fresh code

ResendVerification SHALL issue a new verification code and send it to the registered address of the User with the given provider user ID, even when no earlier code was ever issued. The email SHALL be the one SendVerification sends: in the User's preferred language (Japanese when none is set), in the name of Liverty Music, with a link to the email verification screen carrying the User and the new code. It SHALL fail with FailedPrecondition when the address is already verified, and with Internal on any other failure to issue or send.

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
