# Organizer.ListArtists

## Purpose

Returns the Artists an Organizer currently represents.

## Requirements

### Requirement: ListArtists returns the roster in a stable order

ListArtists SHALL return every Artist linked to the Organizer, ordered by ArtistId ascending, which is the order in which the Artists were first registered, so the same roster is returned in the same order on every call. It SHALL return an empty list when the Organizer represents no Artist, or when no Organizer has the id.

#### Scenario: Organizer with Artists

- **WHEN** the Organizer represents three Artists
- **THEN** ListArtists returns the three Artists, ordered by ArtistId

#### Scenario: Roster order is stable

- **WHEN** ListArtists is called twice with no change to the roster
- **THEN** both calls return the Artists in the same order

#### Scenario: Empty roster

- **WHEN** the Organizer represents no Artist
- **THEN** ListArtists returns an empty list
