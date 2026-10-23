## MODIFIED Requirements

### Requirement: ResendEmailVerification is decided by the usecase

ResendEmailVerification SHALL call UserUseCase.ResendEmailVerification with the caller's sign-in identity and return its failure unchanged. Resolving the caller, the limit of 3 resends per 10 minutes per User and announcing the resend request are that usecase's rules; the code itself is sent later by UserUseCase.ReissueEmailVerification.

#### Scenario: Caller resends their own email

- **WHEN** a signed-in caller requests a resend for their own unverified account
- **THEN** the call succeeds once UserUseCase.ResendEmailVerification has announced the resend request for the caller's User

#### Scenario: Usecase failure returned unchanged

- **WHEN** UserUseCase.ResendEmailVerification fails with ResourceExhausted
- **THEN** ResendEmailVerification fails with ResourceExhausted
