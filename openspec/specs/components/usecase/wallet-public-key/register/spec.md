# components/usecase/wallet-public-key/register Specification

## Purpose
WalletPublicKeyUseCase.Register records the public key of the key pair the calling fan's device created for showing tickets, so the device can later make entry QR codes without a connection.

## Requirements

### Requirement: The caller's device becomes the one that shows tickets

Register SHALL take the calling fan, a public key and the current time, and store it with WalletPublicKey.Register, which makes it the fan's only key; an invalid key fails as Register fails. It SHALL require nothing beyond the fan's existing sign-in and SHALL return the registered time and whether a different device's key was replaced. A code signed on a device whose key was replaced SHALL from then on be refused at the venue.

#### Scenario: First time on a phone

- **WHEN** a signed-in fan's phone registers its public key
- **THEN** the key is the fan's key and the phone can show entry QR codes offline from then on

#### Scenario: Fan moves to a new phone

- **WHEN** the fan's new phone registers its key
- **THEN** the new key is the fan's key and codes from the old phone are refused at the venue

#### Scenario: Not a P-256 key

- **WHEN** the given public key is not a valid P-256 key
- **THEN** Register fails with InvalidArgument and the fan's key is unchanged
