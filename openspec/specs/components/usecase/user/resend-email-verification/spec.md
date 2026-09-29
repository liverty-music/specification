# components/usecase/user/resend-email-verification Specification

## Purpose
UserUseCase.ResendEmailVerification sends a fresh verification email to the signed-in caller's own address, at most 3 times per 10 minutes per User, so a fan who lost the first email can still verify it.

## Requirements

### Requirement: Only the caller's own address is sent a fresh verification email

ResendEmailVerification SHALL fail with Unavailable when email verification is not configured, before the caller is resolved. It SHALL then resolve the caller as UserUseCase.ResolveCaller does, with the same failures, and send a fresh verification email through User.ResendVerification with the caller's external id. A FailedPrecondition or Internal failure of User.ResendVerification SHALL be returned unchanged.

#### Scenario: Caller resends their own email

- **WHEN** a signed-in caller requests a resend for their own unverified account
- **THEN** a fresh verification email is sent

#### Scenario: Another user's account

- **WHEN** the named User id is not the caller's
- **THEN** ResendEmailVerification fails with PermissionDenied and nothing is sent

#### Scenario: Already verified

- **WHEN** the caller's address is already verified
- **THEN** ResendEmailVerification fails with FailedPrecondition

#### Scenario: Verification unavailable

- **WHEN** a signed-in caller requests a resend while email verification is not configured
- **THEN** ResendEmailVerification fails with Unavailable, even when the caller has no User

### Requirement: At most 3 resends per 10 minutes per User

After the caller is resolved, each request SHALL count toward a limit of 3 per rolling 10 minutes per User, whether or not the send then succeeds. A request over the limit SHALL fail with ResourceExhausted, send nothing and not count. One User's requests SHALL NOT count toward another User's limit.

#### Scenario: Too many requests

- **WHEN** the same User makes a fourth request within 10 minutes
- **THEN** ResendEmailVerification fails with ResourceExhausted and nothing is sent

#### Scenario: Failed attempts count

- **WHEN** a User's first 3 requests within 10 minutes each fail with FailedPrecondition because the address is already verified
- **THEN** a fourth request within those 10 minutes fails with ResourceExhausted

#### Scenario: Limit is per user

- **WHEN** one User has made 3 requests within 10 minutes and another User makes their first
- **THEN** the other User's verification email is sent
