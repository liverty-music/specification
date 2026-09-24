# Organizer.ListByStatus

## Purpose

Returns every Organizer in one given status.

## Requirements

### Requirement: ListByStatus returns the Organizers in the status by name

ListByStatus SHALL return every Organizer whose status is the given status, ordered by name ascending, and SHALL return an empty list when none is in that status.

#### Scenario: Organizers in the status

- **WHEN** two Organizers are provisioning and one is active
- **THEN** ListByStatus for provisioning returns the two provisioning Organizers, ordered by name

#### Scenario: None in the status

- **WHEN** no Organizer is in the given status
- **THEN** ListByStatus returns an empty list
