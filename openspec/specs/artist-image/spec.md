## Purpose

This capability provides artist image data from fanart.tv, enabling visual identification of artists in the frontend via thumbnails, backgrounds, logos, and banners.

## Requirements

### Requirement: Fanart Entity
The system SHALL define a `Fanart` entity that mirrors the fanart.tv API response structure. The entity SHALL contain the following image collection fields: `ArtistThumb`, `ArtistBackground`, `HDMusicLogo`, `MusicLogo`, `MusicBanner`. Each collection SHALL contain zero or more `FanartImage` entries with `ID`, `URL`, `Likes`, and `Lang` fields. The entity SHALL also contain an optional `LogoColorProfile` field holding the extracted dominant color properties of the best logo image.

#### Scenario: Fanart with all image types populated
- **WHEN** fanart.tv returns data for an artist with all image types
- **THEN** the `Fanart` entity SHALL contain non-empty slices for `ArtistThumb`, `ArtistBackground`, `HDMusicLogo`, `MusicLogo`, and `MusicBanner`

#### Scenario: Fanart with partial image types
- **WHEN** fanart.tv returns data with only some image types (e.g., only `ArtistThumb` and `HDMusicLogo`)
- **THEN** the `Fanart` entity SHALL contain non-empty slices for the available types and empty slices for the missing types

#### Scenario: Fanart with logo analysis
- **WHEN** fanart data includes a logo image that has been analyzed
- **THEN** the `Fanart` entity SHALL contain a non-nil `LogoColorProfile` with `DominantHue`, `DominantLightness`, and `IsChromatic` fields

### Requirement: Best Image Selection
The system SHALL provide a `BestByLikes` function that selects the image with the highest `Likes` count from a given `FanartImage` slice. The function SHALL return an empty string when the input slice is empty.

#### Scenario: Multiple images with different likes
- **WHEN** `BestByLikes` is called with a slice containing images with likes values [3, 7, 1]
- **THEN** the function SHALL return the URL of the image with 7 likes

#### Scenario: Empty image slice
- **WHEN** `BestByLikes` is called with an empty slice
- **THEN** the function SHALL return an empty string

### Requirement: Fanart Proto Message
The system SHALL define a `Fanart` protobuf message within `liverty_music.entity.v1` containing optional URL fields for each image type: `artist_thumb`, `artist_background`, `hd_music_logo`, `music_logo`, `music_banner`. Each field SHALL use a dedicated wrapper message with URI validation. The message SHALL also include an `optional LogoColorProfile logo_color_profile` field. The `Artist` message SHALL include an `optional Fanart fanart` field.

#### Scenario: Artist with fanart data
- **WHEN** an Artist is serialized to proto and fanart data exists
- **THEN** the `fanart` field SHALL contain a `Fanart` message with best image URLs populated for each available image type

#### Scenario: Artist without fanart data
- **WHEN** an Artist is serialized to proto and no fanart data exists
- **THEN** the `fanart` field SHALL be absent (optional not set)

#### Scenario: Artist with logo analysis in fanart
- **WHEN** an Artist is serialized to proto and logo analysis data exists
- **THEN** the `fanart.logo_color_profile` field SHALL contain a `LogoColorProfile` message

### Requirement: Fanart Proto Mapper
The mapper layer SHALL convert the domain `Fanart` entity (with full image arrays) to the proto `Fanart` message (with single best URL per type) using `BestByLikes` for selection. The mapper SHALL also convert the domain `LogoColorProfile` to the proto `LogoColorProfile` message when present.

#### Scenario: Mapper selects best images
- **WHEN** a domain Artist with Fanart data is mapped to proto
- **THEN** each proto Fanart field SHALL contain the URL of the image with the highest likes count from the corresponding domain field

#### Scenario: Mapper includes logo analysis
- **WHEN** a domain Artist with Fanart and LogoColorProfile is mapped to proto
- **THEN** the proto Fanart message SHALL include the `logo_color_profile` field with dominant hue, lightness, and chromaticity

### Requirement: Fanart Database Storage
The system SHALL store fanart.tv API response data in a `fanart` JSONB column on the `artists` table. The system SHALL also store the synchronization timestamp in a `fanart_synced_at` TIMESTAMPTZ column. Logo analysis results SHALL be stored within the same `fanart` JSONB under a `logoColorProfile` key.

#### Scenario: Fanart data persisted with analysis
- **WHEN** fanart data is fetched and logo analysis is performed
- **THEN** the `fanart` JSONB column SHALL contain both the parsed response data and the `logoColorProfile` object, and `fanart_synced_at` SHALL be set to the current timestamp

#### Scenario: Fanart data persisted without analysis
- **WHEN** fanart data is fetched but no logo image is available for analysis
- **THEN** the `fanart` JSONB column SHALL contain the parsed response data without a `logoColorProfile` key

#### Scenario: Fanart data updated
- **WHEN** fanart data is re-fetched for an artist that already has fanart data
- **THEN** the `fanart` JSONB column SHALL be overwritten with the new data and `fanart_synced_at` SHALL be updated

### Requirement: ArtistImageResolver Interface
The system SHALL define an `ArtistImageResolver` interface in the entity layer with a method `ResolveImages(ctx, mbid) (*Fanart, error)` that fetches image data from an external source using the artist's MusicBrainz ID.

#### Scenario: Successful image resolution
- **WHEN** `ResolveImages` is called with a valid MBID that has fanart.tv data
- **THEN** it SHALL return a populated `Fanart` entity

#### Scenario: No images found
- **WHEN** `ResolveImages` is called with an MBID that has no fanart.tv data
- **THEN** it SHALL return `nil` without error

#### Scenario: External service failure
- **WHEN** the external image service is unavailable
- **THEN** it SHALL return an `Unavailable` error

### Requirement: fanart.tv API Client
The system SHALL implement the `ArtistImageResolver` interface using the fanart.tv API v3 endpoint `GET /v3/music/{mbid}`. The client SHALL use the existing throttle and retry patterns (exponential backoff, max 4 retries). Authentication SHALL use a project API key provided via `FANARTTV_API_KEY` environment variable.

#### Scenario: Successful API call
- **WHEN** the client calls fanart.tv with a valid MBID
- **THEN** it SHALL parse the JSON response into a `Fanart` entity

#### Scenario: Artist not found on fanart.tv
- **WHEN** fanart.tv returns HTTP 404 for an MBID
- **THEN** the client SHALL return `nil` without error

#### Scenario: Rate limited
- **WHEN** fanart.tv returns HTTP 429
- **THEN** the client SHALL retry with exponential backoff respecting the `Retry-After` header

### Requirement: Immediate Image Fetch on Artist Creation
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

### Requirement: Periodic Image Sync CronJob
The system SHALL run a daily CronJob (`artist-image-sync`) that refreshes stale fanart data and backfills artists without fanart data. The job SHALL select artists where `fanart IS NULL` (prioritized) or `fanart_synced_at` is older than 7 days. The job SHALL use a circuit breaker pattern (stop after 3 consecutive failures).

#### Scenario: Backfill artist without fanart
- **WHEN** the CronJob runs and finds artists with `fanart IS NULL`
- **THEN** it SHALL fetch fanart data for each and persist the result

#### Scenario: Refresh stale fanart
- **WHEN** the CronJob runs and finds artists with `fanart_synced_at` older than 7 days
- **THEN** it SHALL re-fetch fanart data and overwrite the existing JSONB

#### Scenario: Circuit breaker activation
- **WHEN** 3 consecutive fanart.tv API calls fail
- **THEN** the job SHALL stop processing remaining artists and exit with code 0

#### Scenario: SIGTERM during processing
- **WHEN** the job receives SIGTERM while processing
- **THEN** the job SHALL stop processing and exit gracefully
