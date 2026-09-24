# User.GetByExternalID

## Purpose

Returns the User linked to a given identity at the identity provider, including its Home when one is set.

## Requirements

### Requirement: GetByExternalID returns the user or NotFound

GetByExternalID SHALL return the User whose external id equals the given value, carrying its Home, centroid included, when one is set. It SHALL fail with NotFound when no User has that external id, and with InvalidArgument when the value is empty. Any other failure to read SHALL be returned with its own code, not as NotFound.

#### Scenario: Registered identity

- **WHEN** GetByExternalID runs for the external id of a stored User
- **THEN** it returns that User with its Home, if any

#### Scenario: Unregistered identity

- **WHEN** no User has the given external id
- **THEN** GetByExternalID fails with NotFound

#### Scenario: Empty external id

- **WHEN** the external id is empty
- **THEN** GetByExternalID fails with InvalidArgument
