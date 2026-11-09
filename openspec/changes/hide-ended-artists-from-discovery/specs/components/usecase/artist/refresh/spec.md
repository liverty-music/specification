# Spec Delta

## Purpose

ArtistUseCase.Refresh reads an artist again from the music catalog and keeps the catalog's canonical name and whether the artist's activity has ended, so every artist shows the catalog's name and charts and similar artists stop suggesting artists whose activity has ended. It runs when an artist is newly registered, and daily for one thirtieth of all artists.

## ADDED Requirements

### Requirement: Refresh adopts the catalog's name and activity status
ArtistUseCase.Refresh SHALL take an artist id, MBID and the artist's current name and look the MBID up with Artist.GetArtist. When the catalog's name is not empty and differs from the current name, it SHALL set it with Artist.UpdateName; when the catalog's name is empty or equal to the current name, the name SHALL not change. It SHALL then set the artist's activity_ended to the returned activity status with Artist.UpdateActivityEnded. When Artist.GetArtist fails with NotFound (the catalog has no artist for the MBID), Refresh SHALL change nothing and succeed.

#### Scenario: Catalog name differs
- **WHEN** the current name is "the band" and the catalog's name is "The Band"
- **THEN** the artist's name becomes "The Band"

#### Scenario: Catalog name equal
- **WHEN** the catalog's name equals the current name
- **THEN** the name is not updated

#### Scenario: Catalog name empty
- **WHEN** the catalog returns an empty name
- **THEN** the name is not updated and Refresh does not fail

#### Scenario: Catalog marks the activity as ended
- **WHEN** the artist's activity_ended is false and Artist.GetArtist returns activity ended true
- **THEN** the artist's activity_ended becomes true

#### Scenario: Catalog no longer marks the activity as ended
- **WHEN** the artist's activity_ended is true and Artist.GetArtist returns activity ended false
- **THEN** the artist's activity_ended becomes false

#### Scenario: MBID unknown to the catalog
- **WHEN** Artist.GetArtist fails with NotFound
- **THEN** Refresh succeeds and neither the name nor activity_ended changes

### Requirement: Refresh reports failures
ArtistUseCase.Refresh SHALL fail with the error of Artist.GetArtist, other than NotFound, without changing the name or activity_ended, and SHALL fail with the error of Artist.UpdateName or Artist.UpdateActivityEnded.

#### Scenario: Catalog unavailable
- **WHEN** Artist.GetArtist fails with Unavailable
- **THEN** Refresh fails with Unavailable and the name and activity_ended are unchanged

#### Scenario: Artist gone
- **WHEN** Artist.UpdateActivityEnded fails with NotFound
- **THEN** Refresh fails with NotFound

### Requirement: Refresh runs when an artist is newly registered
When an artist-created announcement is made, Refresh SHALL run with the announced artist id, MBID and name. When the run fails, it SHALL be retried up to 3 more times.

#### Scenario: Artist announced
- **WHEN** an artist-created announcement is made for an artist
- **THEN** Refresh runs with that artist's id, MBID and announced name

### Requirement: Refresh runs daily over a 30-day rotation
Once a day at 05:00 Japan time, Refresh SHALL run, one artist at a time, for the artists returned by Artist.ListRefreshDue with a slot count of 30 and the slot equal to the number of whole days from 1970-01-01 to the run's date in Japan time, modulo 30. The run SHALL stop after 3 consecutive failed artists and SHALL stop when it is asked to shut down; a failed artist does not stop the run otherwise, and it is read again on its slot's next day, 30 days later.

#### Scenario: Run picks today's slot
- **WHEN** the run starts on 2026-11-10 in Japan time, 20,767 days after 1970-01-01
- **THEN** it refreshes the artists in slot 7 of 30

#### Scenario: Every artist within 30 days
- **WHEN** the run succeeds on 30 consecutive days
- **THEN** every artist registered before the first of those runs has been refreshed once

#### Scenario: Consecutive failures
- **WHEN** the catalog is unreachable for 3 artists in a row
- **THEN** the run stops and those artists keep their current name and activity_ended
