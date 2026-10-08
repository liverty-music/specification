# Spec Delta

## ADDED Requirements

### Requirement: RegisterWalletPublicKey is for the signed-in fan only

RegisterWalletPublicKey SHALL require a signed-in caller and fail with Unauthenticated otherwise. It SHALL resolve the caller to their stored User (User.GetByExternalID), failing with NotFound when the caller has no stored account, and pass that User to WalletPublicKeyUseCase.Register; the request never names a User. It SHALL fail with InvalidArgument when the public key is missing.

#### Scenario: Fan's phone registers its key

- **WHEN** a signed-in fan calls RegisterWalletPublicKey with their phone's public key
- **THEN** the key is registered for that fan

#### Scenario: Not signed in

- **WHEN** a caller who is not signed in calls RegisterWalletPublicKey
- **THEN** the call fails with Unauthenticated

#### Scenario: Missing key

- **WHEN** RegisterWalletPublicKey is called without a public key
- **THEN** it fails with InvalidArgument
