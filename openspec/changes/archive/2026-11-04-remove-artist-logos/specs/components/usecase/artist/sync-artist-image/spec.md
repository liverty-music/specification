## ADDED Requirements

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

## REMOVED Requirements

### Requirement: SyncArtistImage records the artist's images and logo profile
**Reason**: SyncArtistImage no longer obtains or profiles a logo; "SyncArtistImage records the artist's images" replaces it.
**Migration**: None.

### Requirement: A logo failure does not stop the sync
**Reason**: SyncArtistImage no longer obtains a logo.
**Migration**: None.
