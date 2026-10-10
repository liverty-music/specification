# Spec Delta

## Purpose

Stores a User's WalletPublicKey, replacing the key of the device that showed tickets before.

## ADDED Requirements

### Requirement: Register keeps one key per user

Register SHALL take a User, a public key and a time, and make that public key the User's WalletPublicKey with that registered time, replacing any earlier one in one step, so that the User never has two keys. It SHALL report whether it replaced a different public key. Registering the public key the User already has SHALL change nothing and report that nothing was replaced. It SHALL fail with InvalidArgument when the public key is invalid.

#### Scenario: First device

- **WHEN** a User with no key registers K1
- **THEN** K1 is the User's key and nothing was replaced

#### Scenario: New phone

- **WHEN** a User whose key is K1 registers K2 at 10:00
- **THEN** K2 is the User's key with registered time 10:00, and Register reports that it replaced a key

#### Scenario: Same key again

- **WHEN** a User whose key is K1 registers K1 again
- **THEN** nothing changes and Register reports that nothing was replaced

#### Scenario: Invalid key

- **WHEN** a public key that is not a P-256 point is registered
- **THEN** Register fails with InvalidArgument and the User's key is unchanged
