## MODIFIED Requirements

### Requirement: Fanart Entity
The system SHALL define a `Fanart` entity that mirrors the fanart.tv API response structure. The entity SHALL contain the following image collection fields: `ArtistThumb`, `ArtistBackground`, `HDMusicLogo`, `MusicLogo`, `MusicBanner`. Each collection SHALL contain zero or more `FanartImage` entries with `ID`, `URL`, `Likes`, and `Lang` fields. The entity SHALL also contain an optional `LogoAnalysis` field holding the extracted dominant color properties of the best logo image.

#### Scenario: Fanart with all image types populated
- **WHEN** fanart.tv returns data for an artist with all image types
- **THEN** the `Fanart` entity SHALL contain non-empty slices for `ArtistThumb`, `ArtistBackground`, `HDMusicLogo`, `MusicLogo`, and `MusicBanner`

#### Scenario: Fanart with partial image types
- **WHEN** fanart.tv returns data with only some image types (e.g., only `ArtistThumb` and `HDMusicLogo`)
- **THEN** the `Fanart` entity SHALL contain non-empty slices for the available types and empty slices for the missing types

#### Scenario: Fanart with logo analysis
- **WHEN** fanart data includes a logo image that has been analyzed
- **THEN** the `Fanart` entity SHALL contain a non-nil `LogoAnalysis` with `DominantHue`, `DominantLightness`, and `IsChromatic` fields

### Requirement: Fanart Proto Message
The system SHALL define a `Fanart` protobuf message within `liverty_music.entity.v1` containing optional URL fields for each image type: `artist_thumb`, `artist_background`, `hd_music_logo`, `music_logo`, `music_banner`. Each field SHALL use a dedicated wrapper message with URI validation. The message SHALL also include an `optional LogoAnalysis logo_analysis` field. The `Artist` message SHALL include an `optional Fanart fanart` field.

#### Scenario: Artist with fanart data
- **WHEN** an Artist is serialized to proto and fanart data exists
- **THEN** the `fanart` field SHALL contain a `Fanart` message with best image URLs populated for each available image type

#### Scenario: Artist without fanart data
- **WHEN** an Artist is serialized to proto and no fanart data exists
- **THEN** the `fanart` field SHALL be absent (optional not set)

#### Scenario: Artist with logo analysis in fanart
- **WHEN** an Artist is serialized to proto and logo analysis data exists
- **THEN** the `fanart.logo_analysis` field SHALL contain a `LogoAnalysis` message

### Requirement: Fanart Proto Mapper
The mapper layer SHALL convert the domain `Fanart` entity (with full image arrays) to the proto `Fanart` message (with single best URL per type) using `BestByLikes` for selection. The mapper SHALL also convert the domain `LogoAnalysis` to the proto `LogoAnalysis` message when present.

#### Scenario: Mapper selects best images
- **WHEN** a domain Artist with Fanart data is mapped to proto
- **THEN** each proto Fanart field SHALL contain the URL of the image with the highest likes count from the corresponding domain field

#### Scenario: Mapper includes logo analysis
- **WHEN** a domain Artist with Fanart and LogoAnalysis is mapped to proto
- **THEN** the proto Fanart message SHALL include the `logo_analysis` field with dominant hue, lightness, and chromaticity

### Requirement: Fanart Database Storage
The system SHALL store fanart.tv API response data in a `fanart` JSONB column on the `artists` table. The system SHALL also store the synchronization timestamp in a `fanart_synced_at` TIMESTAMPTZ column. Logo analysis results SHALL be stored within the same `fanart` JSONB under a `logoAnalysis` key.

#### Scenario: Fanart data persisted with analysis
- **WHEN** fanart data is fetched and logo analysis is performed
- **THEN** the `fanart` JSONB column SHALL contain both the parsed response data and the `logoAnalysis` object, and `fanart_synced_at` SHALL be set to the current timestamp

#### Scenario: Fanart data persisted without analysis
- **WHEN** fanart data is fetched but no logo image is available for analysis
- **THEN** the `fanart` JSONB column SHALL contain the parsed response data without a `logoAnalysis` key
