# Spec Delta

## Purpose

Reads the WalletPublicKey a User's AdmissionCodes are checked against.

## ADDED Requirements

### Requirement: The user's active key

GetActiveByUser SHALL return the User's Active WalletPublicKey and SHALL fail with NotFound when the User has none.

#### Scenario: User with a key

- **WHEN** the User's Active key is K2 and K1 was replaced
- **THEN** K2 is returned

#### Scenario: User without a key

- **WHEN** the User never registered a key
- **THEN** GetActiveByUser fails with NotFound
