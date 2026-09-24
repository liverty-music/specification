# UserUseCase.Delete

## Purpose

Removes a User from the platform. No fan, admin or organizer interface exposes it.

## Requirements

### Requirement: Delete removes the user

Delete SHALL call User.Delete with the given id; a failure of User.Delete, such as NotFound for an unknown User, SHALL be returned as it is.

#### Scenario: Existing user

- **WHEN** Delete is called with a stored User's id
- **THEN** the User no longer exists

#### Scenario: Unknown user

- **WHEN** no User has the given id
- **THEN** Delete fails with NotFound
