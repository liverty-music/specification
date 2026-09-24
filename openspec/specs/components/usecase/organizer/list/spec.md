# OrganizerUseCase.List

## Purpose

OrganizerUseCase.List returns every Organizer, whatever its status, so an admin can see all Organizers on the organizer-management screen.

## Requirements

### Requirement: List returns every Organizer

List SHALL return the Organizers through Organizer.List, including those that are provisioning or deactivated.

#### Scenario: Organizers in every status

- **WHEN** an active, a provisioning and a deactivated Organizer exist
- **THEN** List returns all three

#### Scenario: No Organizers

- **WHEN** no Organizer exists
- **THEN** List returns an empty list
