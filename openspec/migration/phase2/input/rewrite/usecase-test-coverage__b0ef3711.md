<!-- spec: usecase-test-coverage | target: components/usecase/artist/sync-artist-image | flags: CLASSNAME | new_name: Artist image sync resolves image, logo color, and fanart update with graceful degradation -->

### Requirement: ArtistImageSyncUsecase SyncArtistImage Tests

The test suite SHALL verify that `ArtistImageSyncUsecase.SyncArtistImage()` correctly orchestrates artist fetch, image resolution, logo color analysis, and fanart update.

#### Scenario: Sync with valid MBID

- **WHEN** `SyncArtistImage()` is called for an artist with a valid MusicBrainz ID
- **THEN** the image resolver SHALL be called to resolve the image URL
- **AND** the logo image fetcher SHALL be called to download and analyze the logo
- **AND** the fanart record SHALL be updated with the resolved image URL and logo color

#### Scenario: Sync with empty MBID

- **WHEN** `SyncArtistImage()` is called for an artist with an empty MusicBrainz ID
- **THEN** the system SHALL return early without error
- **AND** the image resolver SHALL NOT be called

#### Scenario: Sync when image resolver returns NotFound

- **WHEN** `SyncArtistImage()` is called for a valid artist
- **AND** the image resolver returns a `NotFound` error
- **THEN** the fanart record SHALL be updated with nil image URL (marking the artist as synced)
- **AND** the system SHALL NOT return an error

#### Scenario: Sync when logo fetch fails

- **WHEN** `SyncArtistImage()` is called for a valid artist
- **AND** the image is resolved successfully
- **AND** the logo image fetcher returns an error
- **THEN** the fanart record SHALL be updated with the resolved image URL but without logo color data
- **AND** the system SHALL NOT return an error

#### Scenario: Sync when artist repository returns error

- **WHEN** `SyncArtistImage()` is called
- **AND** the artist repository returns an error when fetching the artist
- **THEN** the system SHALL propagate the error
- **AND** no fanart update SHALL occur
