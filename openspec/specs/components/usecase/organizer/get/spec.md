# OrganizerUseCase.Get

## Purpose

OrganizerUseCase.Get returns one Organizer by its id, whatever its status, so an admin can inspect it.

## Requirements

### Requirement: Get returns the Organizer by id

Get SHALL return the Organizer through Organizer.Get, in any status, and SHALL fail with NotFound when it does not exist.

#### Scenario: Deactivated Organizer

- **WHEN** Get is called for a deactivated Organizer
- **THEN** it returns the Organizer

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** Get fails with NotFound
