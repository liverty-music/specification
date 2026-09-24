# OrganizerUseCase.ListArtists

## Purpose

OrganizerUseCase.ListArtists returns the Artists an Organizer currently represents, for the admin's organizer screen and for the Organizer's own roster.

## Requirements

### Requirement: ListArtists returns the roster of an existing Organizer

ListArtists SHALL check that the Organizer exists through Organizer.Get, failing with NotFound when it does not, and SHALL return its roster through Organizer.ListArtists, whatever its status.

#### Scenario: Organizer with Artists

- **WHEN** ListArtists is called for an Organizer that represents two Artists
- **THEN** it returns the two Artists

#### Scenario: Deactivated Organizer

- **WHEN** ListArtists is called for a deactivated Organizer
- **THEN** it returns an empty list, because deactivation freed its Artists

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** ListArtists fails with NotFound
