# Spec Delta

## ADDED Requirements

### Requirement: A fresh verification email goes to the caller's own address

ResendEmailVerification SHALL fail with Unavailable when email verification is not configured, before the caller is resolved. It SHALL then resolve the caller as UserUseCase.ResolveCaller does, with the same failures, and send a fresh verification email through User.ResendVerification with the caller's external id. A FailedPrecondition or Internal failure of User.ResendVerification SHALL be returned unchanged.

#### Scenario: Caller resends their own email
- **WHEN** a signed-in caller requests a resend for their own unverified account
- **THEN** a fresh verification email is sent to the caller's address

#### Scenario: Caller already verified
- **WHEN** the caller's address is already verified
- **THEN** ResendEmailVerification fails with FailedPrecondition

#### Scenario: Email verification not configured
- **WHEN** a signed-in caller requests a resend while email verification is not configured
- **THEN** ResendEmailVerification fails with Unavailable, even when the caller has no User

## REMOVED Requirements

### Requirement: Only the caller's own address is sent a fresh verification email
**Reason**: The request no longer names a User id, so the PermissionDenied case for another User's id is gone.
**Migration**: Replaced by "A fresh verification email goes to the caller's own address".
