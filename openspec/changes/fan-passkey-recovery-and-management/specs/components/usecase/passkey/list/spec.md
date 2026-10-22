## Purpose

PasskeyUseCase.List returns the recorded passkeys of the signed-in fan, each with its provider name and registration time, for passkey management.

## ADDED Requirements

### Requirement: List returns the fan's recorded passkeys

List SHALL take the fan's User and return the result of Passkey.ListByUser for that User, each Passkey with its provider name when it has one. A passkey of the fan that has no record is not returned; List SHALL NOT read the identity provider.

#### Scenario: Fan with recorded passkeys

- **WHEN** the fan has two recorded Passkeys, one from `Google Password Manager` and one whose AAGUID is all zeros
- **THEN** both are returned, the first with provider name `Google Password Manager` and the second without one

#### Scenario: Fan with no record

- **WHEN** the fan has no recorded Passkey
- **THEN** an empty list is returned
