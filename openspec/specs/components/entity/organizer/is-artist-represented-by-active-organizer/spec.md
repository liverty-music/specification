# Organizer.IsArtistRepresentedByActiveOrganizer

## Purpose

Tells whether an Artist is currently represented by an active Organizer.

## Requirements

### Requirement: Only an active Organizer counts as representation

IsArtistRepresentedByActiveOrganizer SHALL report true when the Artist is linked to an Organizer whose status is active, and false when the Artist is linked to no Organizer or only to one that is provisioning or deactivated. It SHALL fail with Internal when the answer cannot be read.

#### Scenario: Represented by an active Organizer

- **WHEN** the Artist is linked to an active Organizer
- **THEN** it reports true

#### Scenario: Represented by a provisioning Organizer

- **WHEN** the Artist is linked to an Organizer that is provisioning
- **THEN** it reports false

#### Scenario: Not represented

- **WHEN** the Artist is linked to no Organizer
- **THEN** it reports false
