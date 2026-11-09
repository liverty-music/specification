# components/entity/artist/update-activity-ended Specification

## Purpose
Records whether a registered artist's activity has ended, as last read from the music catalog.

## Requirements

### Requirement: UpdateActivityEnded sets the activity status
UpdateActivityEnded SHALL set the activity_ended of the artist with the given id to the given value, true or false, and SHALL fail with NotFound when no artist has the id. Setting the value the artist already has SHALL succeed and change nothing.

#### Scenario: Activity ended
- **WHEN** UpdateActivityEnded is called with true for an artist whose activity_ended is false
- **THEN** the artist's activity_ended is true

#### Scenario: Activity resumed in the catalog
- **WHEN** UpdateActivityEnded is called with false for an artist whose activity_ended is true
- **THEN** the artist's activity_ended is false

#### Scenario: Same value
- **WHEN** UpdateActivityEnded is called with the value the artist already has
- **THEN** it succeeds and the artist is unchanged

#### Scenario: Unknown artist
- **WHEN** UpdateActivityEnded is called with an id no artist has
- **THEN** UpdateActivityEnded fails with NotFound
