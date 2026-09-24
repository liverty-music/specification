# Series.Get

## Purpose

Returns one Series by id, with its cover image and first-party attributes when it has them.

## Requirements

### Requirement: Get by id

Get SHALL return the Series with the given id and its cover Media when it has one; it SHALL fail with NotFound when no Series has that id and with InvalidArgument when no id is given.

#### Scenario: Unknown id
- **WHEN** no Series has the id
- **THEN** Get fails with NotFound

#### Scenario: Empty id
- **WHEN** Get is called with no id
- **THEN** it fails with InvalidArgument
