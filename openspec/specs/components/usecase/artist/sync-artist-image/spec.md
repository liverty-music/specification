# ArtistImageSyncUseCase.SyncArtistImage

## Purpose

ArtistImageSyncUseCase.SyncArtistImage fetches an artist's community images and records the result. It runs when an artist is newly registered and daily for artists whose images were never checked and for followed artists last checked more than 7 days ago.

## Requirements

### Requirement: SyncArtistImage reports lookup and recording failures
ArtistImageSyncUseCase.SyncArtistImage SHALL fail with the error of Artist.ResolveImages without recording anything, and SHALL fail with the error of Artist.UpdateFanart.

#### Scenario: Image catalog unavailable
- **WHEN** Artist.ResolveImages fails with Unavailable
- **THEN** SyncArtistImage fails and nothing is recorded

#### Scenario: Recording fails
- **WHEN** Artist.UpdateFanart fails with NotFound
- **THEN** SyncArtistImage fails with NotFound

### Requirement: SyncArtistImage runs when an artist is newly registered
When an artist-created announcement is made, SyncArtistImage SHALL run for the announced artist id and MBID. When the run fails, it SHALL be retried up to 3 more times.

#### Scenario: Artist announced
- **WHEN** an artist-created announcement is made for an artist
- **THEN** SyncArtistImage runs for that artist

#### Scenario: Run fails
- **WHEN** SyncArtistImage fails for an announced artist
- **THEN** it is run again, at most 3 more times

### Requirement: SyncArtistImage runs daily for due artists
Once a day, SyncArtistImage SHALL run for up to 500 artists returned by Artist.ListStaleOrMissingFanart with an age of 7 days, in the returned order. The daily run SHALL stop after 3 consecutive failed artists, and SHALL stop when it is asked to shut down; a failed artist does not stop the run otherwise.

#### Scenario: Due artists
- **WHEN** the daily run starts and 20 artists are due
- **THEN** SyncArtistImage runs for each of the 20 artists

#### Scenario: Three consecutive failures
- **WHEN** SyncArtistImage fails for 3 artists in a row
- **THEN** the daily run stops without processing the remaining artists

#### Scenario: Isolated failure
- **WHEN** SyncArtistImage fails for one artist and succeeds for the next
- **THEN** the daily run continues

### Requirement: SyncArtistImage records the artist's images
ArtistImageSyncUseCase.SyncArtistImage SHALL take an artist id and MBID, look the images up with Artist.ResolveImages and record the result with Artist.UpdateFanart at the current time. When the MBID is empty, SyncArtistImage SHALL do nothing and SHALL NOT fail.

#### Scenario: Images found
- **WHEN** Artist.ResolveImages returns fanart with an artist_background image
- **THEN** the fanart is recorded with the current check time

#### Scenario: No images
- **WHEN** Artist.ResolveImages returns no fanart
- **THEN** the artist is recorded with no fanart and the current check time, and SyncArtistImage does not fail

#### Scenario: Empty MBID
- **WHEN** SyncArtistImage is called with an empty MBID
- **THEN** no lookup is made, nothing is recorded, and SyncArtistImage does not fail
