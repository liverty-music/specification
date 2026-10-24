## Purpose

Confirms a User's email address at the identity provider with the code from that User's verification email, so the address counts as verified from then on.

## ADDED Requirements

### Requirement: VerifyEmail confirms the address with a valid code

VerifyEmail SHALL take the provider user ID of a User and a code. When the code is the latest one issued for that identity's address and is less than 1 hour old, it SHALL mark the address verified and succeed. A code that is wrong, older than 1 hour or already used SHALL fail with InvalidArgument and change nothing. It SHALL fail with NotFound when no identity has the provider user ID, and with Unavailable when the identity provider cannot be reached.

#### Scenario: Valid code

- **WHEN** VerifyEmail runs with the code emailed 10 minutes ago
- **THEN** the address is verified

#### Scenario: Code already used

- **WHEN** VerifyEmail runs a second time with the same code
- **THEN** it fails with InvalidArgument

#### Scenario: Code older than 1 hour

- **WHEN** VerifyEmail runs with a code emailed 61 minutes ago
- **THEN** it fails with InvalidArgument and the address stays unverified

#### Scenario: Unknown identity

- **WHEN** no identity has the provider user ID
- **THEN** VerifyEmail fails with NotFound
