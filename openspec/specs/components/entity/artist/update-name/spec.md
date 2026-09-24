# Artist.UpdateName

## Purpose

Replaces the display name of a registered artist.

## Requirements

### Requirement: UpdateName replaces the name
UpdateName SHALL set the name of the artist with the given id to the given name and SHALL fail with NotFound when no artist has that id.

#### Scenario: Known artist
- **WHEN** UpdateName is called for a registered artist with a new name
- **THEN** the artist's name is the new name

#### Scenario: Unknown artist
- **WHEN** UpdateName is called with an id no artist has
- **THEN** UpdateName fails with NotFound and no name changes
