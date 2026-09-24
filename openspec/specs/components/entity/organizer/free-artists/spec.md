# Organizer.FreeArtists

## Purpose

Removes every link between an Organizer and the Artists it represents, so each of them can be associated with another Organizer.

## Requirements

### Requirement: FreeArtists releases the whole roster

FreeArtists SHALL remove all of the Organizer's Artist links and SHALL succeed when it has none.

#### Scenario: Organizer with Artists

- **WHEN** the Organizer represents two Artists
- **THEN** both links are removed and each Artist can be associated with another Organizer

#### Scenario: Empty roster

- **WHEN** the Organizer represents no Artist
- **THEN** FreeArtists succeeds and nothing changes
