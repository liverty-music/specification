# User.Get

## Purpose

Returns the User with a given id, including its Home when one is set.

## Requirements

### Requirement: Get returns the user or NotFound

Get SHALL return the User with the given id, carrying its Home, centroid included, when one is set and no home otherwise. It SHALL fail with NotFound when no User has that id, and with InvalidArgument when the id is empty. Any other failure to read SHALL be returned with its own code, not as NotFound.

#### Scenario: User with a home

- **WHEN** Get runs for a User whose home is `JP-13`
- **THEN** it returns the User with that Home

#### Scenario: User without a home

- **WHEN** Get runs for a User who has not set a home
- **THEN** it returns the User with no home

#### Scenario: Unknown id

- **WHEN** no User has the given id
- **THEN** Get fails with NotFound

#### Scenario: Empty id

- **WHEN** the id is empty
- **THEN** Get fails with InvalidArgument
