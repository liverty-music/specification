## REMOVED Requirements

### Requirement: A valid home is stored for the user

**Reason**: A well-formed code that is no first-level Area (`JP-99`) is no longer stored.
**Migration**: "A home of a first-level Area is stored for the user" states the behavior; a client that sent such a code gets InvalidArgument.

## ADDED Requirements

### Requirement: A home of a first-level Area is stored for the user

SetHome SHALL take a User id and a Home, and resolve the Home's level 1 with the Home's country code (Area.Resolve). When the Home is malformed in the terms of the User entity, when Area.Resolve fails with NotFound, or when the Area it returns has a code other than the given level 1, SetHome SHALL fail with InvalidArgument and store nothing. Otherwise it SHALL call User.UpdateHome and return the updated User; a failure of User.UpdateHome, such as NotFound for an unknown User, SHALL be returned as it is.

#### Scenario: Set home area

- **WHEN** SetHome is called with country code `JP` and level 1 `JP-13`
- **THEN** it returns the User with that Home

#### Scenario: Home in a territory without subdivisions

- **WHEN** SetHome is called with country code `HK` and level 1 `HK`
- **THEN** it returns the User with that Home

#### Scenario: Level 1 in another country

- **WHEN** SetHome is called with a Home whose level 1 `US-CA` does not belong to country code `JP`
- **THEN** it fails with InvalidArgument and the User's home is unchanged

#### Scenario: Well-formed code that is no Area

- **WHEN** SetHome is called with country code `JP` and level 1 `JP-99`
- **THEN** it fails with InvalidArgument and the User's home is unchanged

#### Scenario: Lower-level code

- **WHEN** SetHome is called with country code `FR` and level 1 `FR-33`, which resolves to `FR-NAQ`
- **THEN** it fails with InvalidArgument and the User's home is unchanged

#### Scenario: Withdrawn code

- **WHEN** SetHome is called with country code `CN` and level 1 `CN-HK`, which resolves to `HK`
- **THEN** it fails with InvalidArgument and the User's home is unchanged

#### Scenario: Unknown user

- **WHEN** no User has the given id
- **THEN** SetHome fails with NotFound
