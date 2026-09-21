# Sync Artist Image

## Purpose

Fetches and keeps an artist's images up to date, fetching immediately when the artist is created and periodically refreshing stale images, deriving logo color data and degrading gracefully when images are unavailable.

## Requirements

### Requirement: Artist image sync resolves found/absent/unavailable outcomes

Artist image sync SHALL fetch image data from an external source using the artist's MusicBrainz ID, resolving to one of three outcomes: images found, no images found, or the external service unavailable.

#### Scenario: Successful image resolution
- **WHEN** artist image sync runs for an artist with a valid MusicBrainz ID that has matching fanart data
- **THEN** it SHALL return the resolved image data

#### Scenario: No images found
- **WHEN** artist image sync runs for an artist with a valid MusicBrainz ID that has no matching fanart data
- **THEN** it SHALL complete with no images and no error

#### Scenario: External service failure
- **WHEN** the external image service is unavailable
- **THEN** artist image sync SHALL report an unavailable error

### Requirement: Immediate image fetch on artist creation
The system SHALL subscribe to `ARTIST.created` events and asynchronously fetch fanart data for newly created artists. This ensures images are available shortly after onboarding when artists are followed.

#### Scenario: New artist created with MBID
- **WHEN** an `ARTIST.created` event is received with a non-empty MBID
- **THEN** the consumer SHALL call `ArtistImageResolver.ResolveImages` and persist the result via `ArtistRepository.UpdateFanart`

#### Scenario: fanart.tv has no data for the artist
- **WHEN** `ResolveImages` returns nil for the new artist
- **THEN** the consumer SHALL update `fanart_synced_at` to the current time without setting fanart data

#### Scenario: fanart.tv is unavailable
- **WHEN** `ResolveImages` returns an error
- **THEN** the consumer SHALL return the error (Watermill retry middleware will retry with exponential backoff, eventually sending to poison queue)

### Requirement: Periodic sync refreshes stale artist images
The system SHALL run a daily job (`artist-image-sync`) that refreshes stale fanart data and backfills artists without fanart data. The job SHALL select artists where `fanart IS NULL` (prioritized) or `fanart_synced_at` is older than 7 days. The job SHALL use a circuit breaker pattern (stop after 3 consecutive failures).

#### Scenario: Backfill artist without fanart
- **WHEN** the job runs and finds artists with `fanart IS NULL`
- **THEN** it SHALL fetch fanart data for each and persist the result

#### Scenario: Refresh stale fanart
- **WHEN** the job runs and finds artists with `fanart_synced_at` older than 7 days
- **THEN** it SHALL re-fetch fanart data and overwrite the existing record

#### Scenario: Circuit breaker activation
- **WHEN** 3 consecutive fanart.tv API calls fail
- **THEN** the job SHALL stop processing remaining artists and exit with code 0

#### Scenario: SIGTERM during processing
- **WHEN** the job receives SIGTERM while processing
- **THEN** the job SHALL stop processing and exit gracefully

### Requirement: Logo Color Analysis and Sync Pipeline Integration

The system SHALL analyze artist logo images (clearLOGO PNGs) to extract
dominant color properties. The analysis SHALL decode the PNG, iterate all
non-transparent pixels (alpha >= 10), convert each pixel from sRGB to OKLCH
color space, and classify pixels as chromatic (chroma > 0.04) or achromatic.
The fanart sync pipeline (CronJob and ARTIST.created consumer) SHALL perform
this logo color analysis after fetching fanart data, using the best logo
image selected by highest likes count from `HDMusicLogo`, falling back to
`MusicLogo` if `HDMusicLogo` is empty.

#### Scenario: Chromatic logo (e.g., colored text/symbol)
- **WHEN** a logo image has more than 30% of non-transparent pixels with OKLCH chroma > 0.04
- **THEN** the analysis SHALL return `isChromatic = true`, `dominantHue` as the peak of a 36-bin (10° each) hue histogram, and `dominantLightness` as the mean lightness of all non-transparent pixels

#### Scenario: Achromatic light logo (e.g., white text)
- **WHEN** a logo image has 30% or fewer chromatic pixels and a mean lightness > 0.6
- **THEN** the analysis SHALL return `isChromatic = false`, `dominantHue` absent (not set), and `dominantLightness` reflecting the high lightness value

#### Scenario: Achromatic dark logo (e.g., black text)
- **WHEN** a logo image has 30% or fewer chromatic pixels and a mean lightness ≤ 0.6
- **THEN** the analysis SHALL return `isChromatic = false`, `dominantHue` absent (not set), and `dominantLightness` reflecting the low lightness value

#### Scenario: Fully transparent image
- **WHEN** a logo image has no non-transparent pixels (alpha >= 10)
- **THEN** the analysis SHALL return nil (no analysis possible)

#### Scenario: Artist has HDMusicLogo
- **WHEN** fanart data is fetched and HDMusicLogo contains images
- **THEN** the sync pipeline SHALL download the best HDMusicLogo image (by likes), run color analysis, and store the result in the `logoColorProfile` field of the fanart JSONB

#### Scenario: Artist has only MusicLogo
- **WHEN** fanart data is fetched and HDMusicLogo is empty but MusicLogo contains images
- **THEN** the sync pipeline SHALL download the best MusicLogo image and run color analysis

#### Scenario: Artist has no logo images
- **WHEN** fanart data is fetched but neither HDMusicLogo nor MusicLogo contain images
- **THEN** the sync pipeline SHALL store fanart data without a `logoColorProfile` field

#### Scenario: Logo image download fails
- **WHEN** the logo image HTTP request fails or returns non-200
- **THEN** the sync pipeline SHALL log a warning and store fanart data without a `logoColorProfile` field (non-fatal)

### Requirement: Artist image sync resolves image, logo color, and fanart update with graceful degradation

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
