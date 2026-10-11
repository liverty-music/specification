# ArtistUseCase.ListByOrganizer

## Purpose

ArtistUseCase.ListByOrganizer returns the Artists an Organizer currently represents. It checks no ownership: the admin's organizer screen names any Organizer, and the organizer console's artist call passes the caller's own Organizer.

## Requirements

### Requirement: ListByOrganizer returns the roster of an existing Organizer

ListByOrganizer SHALL check that the Organizer exists through Organizer.Get, failing with NotFound when it does not, and SHALL return its roster through Organizer.ListArtists, whatever its status.

#### Scenario: Organizer with Artists

- **WHEN** ListByOrganizer is called for an Organizer that represents two Artists
- **THEN** it returns the two Artists

#### Scenario: Deactivated Organizer

- **WHEN** ListByOrganizer is called for a deactivated Organizer
- **THEN** it returns an empty list, because deactivation freed its Artists

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** ListByOrganizer fails with NotFound
