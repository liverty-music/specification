# UserUseCase.Get

## Purpose

Returns a User by its platform id, including its home area and preferred language.

## Requirements

### Requirement: Get returns the user by id

Get SHALL call User.Get with the given id and return the User. A missing User SHALL fail with NotFound, and any other failure to read SHALL be returned with its own code.

Known defect: liverty-music/backend#471

#### Scenario: Existing user

- **WHEN** Get is called with the id of a stored User
- **THEN** it returns that User with its Home, if any

#### Scenario: Unknown id

- **WHEN** no User has the given id
- **THEN** Get fails with NotFound

#### Scenario: Store unavailable

- **WHEN** User.Get fails with Unavailable
- **THEN** Get fails with Unavailable
