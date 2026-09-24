# Organizer.Get

## Purpose

Returns one Organizer by its id, whatever its status.

## Requirements

### Requirement: Get returns the Organizer with the id

Get SHALL return the Organizer with the given id in any status, and SHALL fail with NotFound when no Organizer has that id.

#### Scenario: Existing Organizer

- **WHEN** an Organizer with the id exists, in any status
- **THEN** Get returns it

#### Scenario: Unknown id

- **WHEN** no Organizer has the id
- **THEN** Get fails with NotFound
