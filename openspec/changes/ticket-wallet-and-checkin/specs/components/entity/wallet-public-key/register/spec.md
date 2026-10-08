# Spec Delta

## Purpose

Stores a User's new WalletPublicKey and retires the one it replaces.

## ADDED Requirements

### Requirement: Register keeps one active key per user

Register SHALL take a User, a public key and a time, store a new Active WalletPublicKey with that registered time, and make the User's previously Active key Replaced with that time, in one step, so that the User never has two Active keys. Registering the public key that is already the User's Active key SHALL change nothing and return it. It SHALL fail with InvalidArgument when the public key is invalid.

#### Scenario: First device

- **WHEN** a User with no key registers K1
- **THEN** K1 is stored Active

#### Scenario: New phone

- **WHEN** a User whose Active key is K1 registers K2 at 10:00
- **THEN** K2 is Active and K1 is Replaced at 10:00

#### Scenario: Same key again

- **WHEN** a User whose Active key is K1 registers K1 again
- **THEN** nothing changes and K1 is returned

#### Scenario: Invalid key

- **WHEN** a public key that is not a P-256 point is registered
- **THEN** Register fails with InvalidArgument and the User's Active key is unchanged
