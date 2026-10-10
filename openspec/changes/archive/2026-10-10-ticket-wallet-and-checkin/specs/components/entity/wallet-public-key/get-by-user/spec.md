# Spec Delta

## Purpose

Reads the WalletPublicKey a User's AdmissionCodes are checked against.

## ADDED Requirements

### Requirement: The user's key

GetByUser SHALL return the User's WalletPublicKey and SHALL fail with NotFound when the User has none.

#### Scenario: User with a key

- **WHEN** the User registered K1 and then K2
- **THEN** K2 is returned

#### Scenario: User without a key

- **WHEN** the User never registered a key
- **THEN** GetByUser fails with NotFound
