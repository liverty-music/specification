# UserUseCase.UpdateHome

## Purpose

Sets or changes a User's home area, the baseline for classifying concerts as Home, Nearby or Away, and returns the updated User.

## Requirements

### Requirement: A valid home is stored for the user

UpdateHome SHALL take a User id and a Home. When the Home is invalid in the terms of the User entity, it SHALL fail with InvalidArgument and store nothing. Otherwise it SHALL call User.UpdateHome and return the updated User; a failure of User.UpdateHome, such as NotFound for an unknown User, SHALL be returned as it is.

#### Scenario: Set home area

- **WHEN** UpdateHome is called with a valid Home of level 1 `JP-13`
- **THEN** it returns the User with that Home

#### Scenario: Invalid home

- **WHEN** UpdateHome is called with a Home whose level 1 `US-CA` does not belong to country code `JP`
- **THEN** it fails with InvalidArgument and the User's home is unchanged

#### Scenario: Well-formed code outside the catalog

- **WHEN** UpdateHome is called with country code `JP` and level 1 `JP-99`
- **THEN** the Home is stored

#### Scenario: Unknown user

- **WHEN** no User has the given id
- **THEN** UpdateHome fails with NotFound
