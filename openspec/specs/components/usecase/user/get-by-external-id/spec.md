# UserUseCase.GetByExternalID

## Purpose

Returns the User registered for a given identity at the identity provider, so a signed-in person can be resolved to their User and read their own profile on any device.

## Requirements

### Requirement: GetByExternalID resolves an identity to its user

GetByExternalID SHALL call User.GetByExternalID with the given external id and return the User, with its Home when one is set and with no home otherwise. An identity with no User SHALL fail with NotFound, and any other failure to read SHALL be returned with its own code.

#### Scenario: User with a home

- **WHEN** GetByExternalID is called for a registered identity whose User's home is `JP-13`
- **THEN** it returns that User with its Home

#### Scenario: User without a home

- **WHEN** GetByExternalID is called for a registered identity whose User has not set a home
- **THEN** it returns that User with no home

#### Scenario: Unregistered identity

- **WHEN** no User has the given external id
- **THEN** GetByExternalID fails with NotFound

#### Scenario: Store unavailable

- **WHEN** User.GetByExternalID fails with Unavailable
- **THEN** GetByExternalID fails with Unavailable
