# IdentityVerification.GetByUserID

## Purpose

Returns the identity verification of an account, with its status.

## Requirements

### Requirement: The account's current verification

GetByUserID SHALL return the account's IdentityVerification, preferring an Active one and otherwise the most recently verified one, and SHALL fail with NotFound when the account has never verified.

#### Scenario: Verified account

- **WHEN** the account has an Active IdentityVerification
- **THEN** it is returned with status Active

#### Scenario: Verification lapsed

- **WHEN** the account's only IdentityVerification needs re-verification
- **THEN** it is returned with status NeedsReverification

#### Scenario: Never verified

- **WHEN** the account has no IdentityVerification
- **THEN** it fails with NotFound
