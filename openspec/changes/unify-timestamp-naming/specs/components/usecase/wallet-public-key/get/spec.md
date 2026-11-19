# Spec Delta

## MODIFIED Requirements

### Requirement: The fan's current key, read only

Get SHALL take the calling fan and return their WalletPublicKey with WalletPublicKey.GetByUser, failing with NotFound when the fan has none. It SHALL change nothing.

#### Scenario: Fan with an entry device

- **WHEN** a fan whose key is K2 calls Get
- **THEN** K2 is returned with its register time

#### Scenario: Fan without an entry device

- **WHEN** a fan who never registered a key calls Get
- **THEN** Get fails with NotFound
