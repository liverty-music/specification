# Spec Delta

## Purpose

ArtistActivityRefreshUseCase.RefreshActivity keeps each artist's activity status in line with the music catalog, so charts and similar artists stop suggesting artists whose activity has ended. It runs daily for one thirtieth of all artists and for the artists registered in the last 25 hours.

## ADDED Requirements

### Requirement: RefreshActivity records the catalog's activity status
ArtistActivityRefreshUseCase.RefreshActivity SHALL take an artist id and MBID, look the MBID up with Artist.GetArtist and set the artist's activity_ended to the returned activity status with Artist.UpdateActivityEnded. When Artist.GetArtist fails with NotFound (the catalog has no artist for the MBID), it SHALL leave activity_ended unchanged and succeed.

#### Scenario: Catalog marks the activity as ended
- **WHEN** the artist's activity_ended is false and Artist.GetArtist returns activity ended true
- **THEN** the artist's activity_ended becomes true

#### Scenario: Catalog no longer marks the activity as ended
- **WHEN** the artist's activity_ended is true and Artist.GetArtist returns activity ended false
- **THEN** the artist's activity_ended becomes false

#### Scenario: MBID unknown to the catalog
- **WHEN** Artist.GetArtist fails with NotFound
- **THEN** RefreshActivity succeeds and activity_ended is unchanged

### Requirement: RefreshActivity reports failures
ArtistActivityRefreshUseCase.RefreshActivity SHALL fail with the error of Artist.GetArtist, other than NotFound, without changing activity_ended, and SHALL fail with the error of Artist.UpdateActivityEnded.

#### Scenario: Catalog unreachable
- **WHEN** Artist.GetArtist fails with Unavailable
- **THEN** RefreshActivity fails with Unavailable and activity_ended is unchanged

#### Scenario: Artist gone
- **WHEN** Artist.UpdateActivityEnded fails with NotFound
- **THEN** RefreshActivity fails with NotFound

### Requirement: RefreshActivity runs daily over a 30-day rotation
Once a day at 05:00 Japan time, RefreshActivity SHALL run, one artist at a time, for the artists returned by Artist.ListActivityCheckDue with a slot count of 30, the slot equal to the number of whole days from 1970-01-01 to the run's date in Japan time modulo 30, and the time 25 hours before the run. The run SHALL stop after 3 consecutive failed artists and SHALL stop when it is asked to shut down; a failed artist does not stop the run otherwise, and it is checked again on its slot's next day, 30 days later, unless the run before then lists it.

#### Scenario: Run picks today's slot
- **WHEN** the run starts on 2026-11-10 in Japan time, 20,767 days after 1970-01-01
- **THEN** it checks the artists in slot 7 of 30 and the artists registered after 2026-11-09 04:00 Japan time

#### Scenario: Every artist within 30 days
- **WHEN** the run succeeds on 30 consecutive days
- **THEN** every artist registered before the first of those runs has been checked once

#### Scenario: Newly registered artist
- **WHEN** a chart artist is registered at 12:00 Japan time
- **THEN** the next day's 05:00 run checks it

#### Scenario: Consecutive failures
- **WHEN** the catalog is unreachable for 3 artists in a row
- **THEN** the run stops and those artists keep their current activity_ended
