# Organizer.SetStatus

## Purpose

Sets an Organizer's status, whatever its current status.

## Requirements

### Requirement: SetStatus overwrites the status

SetStatus SHALL set the Organizer's status to the given status without looking at its current status, and SHALL fail with NotFound when the Organizer does not exist.

#### Scenario: Status is set

- **WHEN** an active Organizer is set to deactivated
- **THEN** its status becomes deactivated

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** SetStatus fails with NotFound
