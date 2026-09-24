# Artist.ListStaleOrMissingFanart

## Purpose

Returns the artists whose images are due for a check: never checked, or last checked longer ago than a given age.

## Requirements

### Requirement: ListStaleOrMissingFanart returns due artists, never-checked first
ListStaleOrMissingFanart SHALL return artists that have no fanart_sync_time or whose fanart_sync_time is older than the given age, never-checked artists first and then the oldest check first, and at most the given number of artists. An artist checked within the given age SHALL NOT be returned, whether or not it has images.

#### Scenario: Never-checked and stale artists
- **WHEN** one artist was never checked and another was last checked 8 days ago, and the age is 7 days
- **THEN** both are returned, the never-checked artist first

#### Scenario: Recently checked artist without images
- **WHEN** an artist was checked 2 days ago and no images were found, and the age is 7 days
- **THEN** the artist is not returned

#### Scenario: More due artists than the limit
- **WHEN** 600 artists are due and the limit is 500
- **THEN** 500 artists are returned

#### Scenario: Nothing due
- **WHEN** every artist was checked within the given age
- **THEN** an empty list is returned without error
