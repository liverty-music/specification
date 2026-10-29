## MODIFIED Requirements

### Requirement: Each resend request sends one fresh code to an unverified address

ReissueEmailVerification SHALL run when UserUseCase.ResendEmailVerification starts it, with the caller's User. It SHALL read the User with User.Get and send a fresh code with User.ResendVerification. When User.Get fails with NotFound, or User.ResendVerification fails with FailedPrecondition because the address is already verified, it SHALL finish without sending. When email verification is not configured, it SHALL log that and finish without sending. A step that fails with Unavailable SHALL be tried again; a step tried again after a code was sent sends a newer code. Any other failure SHALL end ReissueEmailVerification with that failure, and it is reported for an admin.

#### Scenario: Unverified address

- **WHEN** ResendEmailVerification starts ReissueEmailVerification for a User whose address is not verified
- **THEN** a fresh verification email is sent to that address

#### Scenario: Already verified

- **WHEN** User.ResendVerification fails with FailedPrecondition
- **THEN** nothing is sent and the request is finished

#### Scenario: Account deleted since the request

- **WHEN** User.Get fails with NotFound
- **THEN** nothing is sent and the request is finished

#### Scenario: Verification not configured

- **WHEN** email verification is not configured in the process that runs ReissueEmailVerification
- **THEN** nothing is sent, the outcome is logged and the request is finished

#### Scenario: Identity provider down

- **WHEN** User.ResendVerification fails with Unavailable
- **THEN** the step is tried again and the code is sent once the identity provider answers

#### Scenario: Identity provider refuses

- **WHEN** User.ResendVerification fails with Internal
- **THEN** ReissueEmailVerification ends with that failure and is reported for an admin
