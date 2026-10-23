# components/usecase/user/resend-email-verification Specification

## Purpose
UserUseCase.ResendEmailVerification sends a fresh verification email to the signed-in caller's own address, at most 3 times per 10 minutes per User, so a fan who lost the first email can still verify it.

## Requirements

### Requirement: At most 3 resends per 10 minutes per User

After the caller is resolved, each request SHALL count toward a limit of 3 per rolling 10 minutes per User. A request over the limit SHALL fail with ResourceExhausted, announce nothing and not count. One User's requests SHALL NOT count toward another User's limit.

#### Scenario: Too many requests

- **WHEN** the same User makes a fourth request within 10 minutes
- **THEN** ResendEmailVerification fails with ResourceExhausted and nothing is announced

#### Scenario: Failed attempts count

- **WHEN** a User's first 3 requests within 10 minutes are all for an address that is already verified, so no email is sent for any of them
- **THEN** a fourth request within those 10 minutes fails with ResourceExhausted

#### Scenario: Limit is per user

- **WHEN** one User has made 3 requests within 10 minutes and another User makes their first
- **THEN** a resend request is announced for the other User

### Requirement: A fresh verification email goes to the caller's own address

ResendEmailVerification SHALL resolve the caller as UserUseCase.ResolveCaller does, with the same failures. It SHALL then announce an email verification resend request for the caller's User and succeed; sending the code is UserUseCase.ReissueEmailVerification's part. A failure to announce SHALL fail the call with Unavailable and SHALL still count toward the limit.

#### Scenario: Caller resends their own email
- **WHEN** a signed-in caller requests a resend for their own unverified account
- **THEN** a resend request is announced for the caller's User and the call succeeds

#### Scenario: Caller already verified
- **WHEN** the caller's address is already verified
- **THEN** the call succeeds and a resend request is announced

#### Scenario: Email verification not configured
- **WHEN** a signed-in caller requests a resend while email verification is not configured
- **THEN** the call succeeds as for any resend request, and no email is sent

#### Scenario: Announcement fails
- **WHEN** the resend request cannot be announced
- **THEN** ResendEmailVerification fails with Unavailable
