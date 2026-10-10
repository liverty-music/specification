# Spec Delta

## Purpose

The fan-facing wallet public key service boundary: how the signed-in fan reads and registers the public key of the device that shows their entry QR code.

## ADDED Requirements

### Requirement: The key is always the signed-in fan's own

Register and Get SHALL require a signed-in caller and fail with Unauthenticated otherwise. They SHALL resolve the caller to their stored User (User.GetByExternalID), failing with NotFound when the caller has no stored account, and pass that User to WalletPublicKeyUseCase.Register or Get; the request never names a User. Register SHALL fail with InvalidArgument, before any usecase runs, when the public key is missing.

#### Scenario: Fan's phone registers its key

- **WHEN** a signed-in fan calls Register with their phone's public key
- **THEN** the key is registered for that fan

#### Scenario: Fan reads their key

- **WHEN** a signed-in fan with a registered key calls Get
- **THEN** that fan's key is returned

#### Scenario: Not signed in

- **WHEN** a caller who is not signed in calls Get
- **THEN** the call fails with Unauthenticated

#### Scenario: Missing key

- **WHEN** Register is called without a public key
- **THEN** it fails with InvalidArgument
