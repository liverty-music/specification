## MODIFIED Requirements

### Requirement: Each resend request sends one fresh code to an unverified address

ReissueEmailVerification SHALL run when UserUseCase.ResendEmailVerification starts it, with the caller's User. It SHALL read the User with User.Get and send a fresh code with User.ResendVerification. When User.Get fails with NotFound, or User.ResendVerification fails with FailedPrecondition because the address is already verified, it SHALL finish without sending. When email verification is not configured, it SHALL log that and finish without sending. Any other failure SHALL fail ReissueEmailVerification so it is run again; a run again after a code was sent sends a newer code.

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

- **WHEN** User.ResendVerification fails with Internal
- **THEN** ReissueEmailVerification fails and runs again
