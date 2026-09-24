# Organizer.List

## Purpose

Returns every Organizer, whatever its status.

## Requirements

### Requirement: List returns every Organizer by name

List SHALL return every Organizer in any status, ordered by name ascending, and SHALL return an empty list when there is none.

#### Scenario: Organizers in every status

- **WHEN** Organizers exist in status provisioning, active and deactivated
- **THEN** List returns all of them, ordered by name

#### Scenario: No Organizers

- **WHEN** no Organizer exists
- **THEN** List returns an empty list
