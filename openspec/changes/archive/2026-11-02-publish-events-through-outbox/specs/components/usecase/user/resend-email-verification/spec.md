## MODIFIED Requirements

### Requirement: At most 3 resends per 10 minutes per User

After the caller is resolved, each request SHALL count toward a limit of 3 per rolling 10 minutes per User. A request over the limit SHALL fail with ResourceExhausted, start nothing and not count. One User's requests SHALL NOT count toward another User's limit.

#### Scenario: Too many requests

- **WHEN** the same User makes a fourth request within 10 minutes
- **THEN** ResendEmailVerification fails with ResourceExhausted and nothing is started

#### Scenario: Failed attempts count

- **WHEN** a User's first 3 requests within 10 minutes are all for an address that is already verified, so no email is sent for any of them
- **THEN** a fourth request within those 10 minutes fails with ResourceExhausted

#### Scenario: Limit is per user

- **WHEN** one User has made 3 requests within 10 minutes and another User makes their first
- **THEN** UserUseCase.ReissueEmailVerification is started for the other User

## REMOVED Requirements

### Requirement: A fresh verification email goes to the caller's own address
**Reason**: An email verification resend request is work for one receiver, not a fact, so it is no longer announced; ResendEmailVerification starts UserUseCase.ReissueEmailVerification directly ("Each allowed request starts one fresh verification email" below).
**Migration**: The trigger of UserUseCase.ReissueEmailVerification changes from the announced resend request to the run ResendEmailVerification starts. A failure to start fails the call with Unavailable, as a failure to announce did.

## ADDED Requirements

### Requirement: Each allowed request starts one fresh verification email

ResendEmailVerification SHALL resolve the caller as UserUseCase.ResolveCaller does, with the same failures. It SHALL then start UserUseCase.ReissueEmailVerification for the caller's User and succeed; sending the code is ReissueEmailVerification's part. The business key of the started work SHALL be the request itself: each request within the limit starts one ReissueEmailVerification, and a second request starts a second one. When ReissueEmailVerification cannot be started, the call SHALL fail with Unavailable and SHALL still count toward the limit.

#### Scenario: Caller resends their own email
- **WHEN** a signed-in caller requests a resend for their own unverified account
- **THEN** ReissueEmailVerification is started for the caller's User and the call succeeds

#### Scenario: Caller already verified
- **WHEN** the caller's address is already verified
- **THEN** the call succeeds and ReissueEmailVerification is started

#### Scenario: Two requests
- **WHEN** a caller makes 2 requests within 10 minutes
- **THEN** ReissueEmailVerification is started twice for the caller's User

#### Scenario: Email verification not configured
- **WHEN** a signed-in caller requests a resend while email verification is not configured
- **THEN** the call succeeds as for any resend request, and no email is sent

#### Scenario: Work cannot be started
- **WHEN** ReissueEmailVerification cannot be started
- **THEN** ResendEmailVerification fails with Unavailable
