# components/usecase/wallet-public-key/get Specification

## Purpose
WalletPublicKeyUseCase.Get tells the calling fan's device which public key is the fan's entry device, so the tickets screen can tell whether it is that device without changing anything.

## Requirements

### Requirement: The fan's current key, read only

Get SHALL take the calling fan and return their WalletPublicKey with WalletPublicKey.GetByUser, failing with NotFound when the fan has none. It SHALL change nothing.

#### Scenario: Fan with an entry device

- **WHEN** a fan whose key is K2 calls Get
- **THEN** K2 is returned with its registered time

#### Scenario: Fan without an entry device

- **WHEN** a fan who never registered a key calls Get
- **THEN** Get fails with NotFound
