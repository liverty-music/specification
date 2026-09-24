# User RPC

## Purpose

The fan-facing user service boundary: who may call each user operation and what the boundary itself decides before any usecase runs.

## Requirements

### Requirement: Resending the caller's verification email

ResendEmailVerification SHALL send a fresh verification email to the signed-in caller's own address through User.ResendVerification. It SHALL fail with Unavailable when email verification is not available (checked before anything else), with Unauthenticated for an unauthenticated caller, with InvalidArgument when no user is given, with NotFound when the caller has no account, and with PermissionDenied when the requested user is not the caller (before any email is sent). Each request that passes the ownership check counts toward a limit of 3 per 10 minutes per user; the fourth fails with ResourceExhausted.

#### Scenario: Caller resends their own email

- **WHEN** a signed-in user requests a resend for their own account
- **THEN** a fresh verification email is sent

#### Scenario: Another user's account

- **WHEN** the requested user is not the caller
- **THEN** it fails with PermissionDenied and nothing is sent

#### Scenario: Too many requests

- **WHEN** the same user makes a fourth request within 10 minutes
- **THEN** it fails with ResourceExhausted

#### Scenario: Not signed in

- **WHEN** the caller is not authenticated
- **THEN** it fails with Unauthenticated

#### Scenario: Caller has no account

- **WHEN** the signed-in caller has no stored account
- **THEN** it fails with NotFound

#### Scenario: Verification unavailable

- **WHEN** email verification is not available
- **THEN** it fails with Unavailable
