## MODIFIED Requirements

### Requirement: ListStaleOrMissingFanart returns due artists, never-checked first
ListStaleOrMissingFanart SHALL return the artists that have no fanart_sync_time, and the artists that at least one fan follows and whose fanart_sync_time is older than the given age. It SHALL return never-checked artists first and then the oldest check first, each artist at most once, and at most the given number of artists. An artist checked within the given age SHALL NOT be returned, whether or not it has images, and an artist that has been checked and that nobody follows SHALL NOT be returned.

#### Scenario: Never-checked and stale artists
- **WHEN** one artist was never checked and another, followed by a fan, was last checked 8 days ago, and the age is 7 days
- **THEN** both are returned, the never-checked artist first

#### Scenario: Never-checked artist nobody follows
- **WHEN** an artist was never checked and nobody follows it
- **THEN** the artist is returned

#### Scenario: Stale artist nobody follows
- **WHEN** an artist was last checked 30 days ago and nobody follows it, and the age is 7 days
- **THEN** the artist is not returned

#### Scenario: Artist followed by several fans
- **WHEN** an artist followed by 3 fans was last checked 8 days ago, and the age is 7 days
- **THEN** the artist is returned once

#### Scenario: Recently checked artist without images
- **WHEN** a followed artist was checked 2 days ago and no images were found, and the age is 7 days
- **THEN** the artist is not returned

#### Scenario: More due artists than the limit
- **WHEN** 600 artists are due and the limit is 500
- **THEN** 500 artists are returned

#### Scenario: Nothing due
- **WHEN** every followed artist was checked within the given age, and every other artist was checked at least once
- **THEN** an empty list is returned without error
