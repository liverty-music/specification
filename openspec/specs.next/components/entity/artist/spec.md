# Artist

## Purpose

Defines the Artist entity, its identity, official site, imagery collected from external sources, derived logo color profile, and the standalone surface for artist operations independent of concerts.

## Requirements

### Requirement: Artist fanart image collection
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

### Requirement: Fanart Image Selection and Mapping

The system SHALL select, for each fanart image type, the image with the
highest likes count from the available images of that type, returning an
empty string when no images are available for that type. When mapping the
domain `Fanart` entity (with full image arrays) to the proto `Fanart` message
(with a single best-by-likes URL per image type), the system SHALL apply this
selection for every image field. The system SHALL also convert the domain
`LogoColorProfile` to the proto `LogoColorProfile` message when present.

#### Scenario: Multiple images with different likes
- **WHEN** images with likes values [3, 7, 1] are available for selection
- **THEN** the function SHALL return the URL of the image with 7 likes

#### Scenario: Empty image slice
- **WHEN** no images are available for selection
- **THEN** the function SHALL return an empty string

#### Scenario: Mapper selects best images
- **WHEN** a domain Artist with Fanart data is mapped to proto
- **THEN** each proto Fanart field SHALL contain the URL of the image with the highest likes count from the corresponding domain field

#### Scenario: Mapper includes logo analysis
- **WHEN** a domain Artist with Fanart and LogoColorProfile is mapped to proto
- **THEN** the proto Fanart message SHALL include the `logo_color_profile` field with dominant hue, lightness, and chromaticity

### Requirement: Artist fanart proto shape
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

### Requirement: Standalone Artist Service
The system SHALL provide a dedicated `ArtistService` that is independent of the `ConcertService` for managing artist-related operations. The service SHALL return Artist entities with populated Fanart data when available.

#### Scenario: Service initialization
- **WHEN** the backend application starts
- **THEN** the `ArtistService` SHALL be registered as a separate RPC handler with its own set of dependencies (repositories, external clients)

#### Scenario: Artist response includes fanart
- **WHEN** any Artist RPC method returns an Artist entity that has Fanart data in the database
- **THEN** the response SHALL include the `fanart` field with best image URLs selected by likes count

#### Scenario: Artist response without fanart
- **WHEN** any Artist RPC method returns an Artist entity without Fanart data
- **THEN** the response SHALL omit the `fanart` field (optional not set)

### Requirement: Artist filtering by MBID

The entity package SHALL provide a `FilterArtistsByMBID(artists []*Artist) []*Artist` function that removes artists with empty MBID and deduplicates by MBID keeping the first occurrence.

#### Scenario: Mixed valid and empty MBIDs

- **WHEN** input contains artists with MBIDs ["abc", "", "def", "abc"]
- **THEN** returns artists with MBIDs ["abc", "def"] in order

#### Scenario: All empty MBIDs

- **WHEN** all artists have empty MBID
- **THEN** returns empty slice

#### Scenario: No duplicates

- **WHEN** all artists have unique non-empty MBIDs
- **THEN** returns all artists unchanged

#### Scenario: Empty input

- **WHEN** input is nil or empty
- **THEN** returns empty slice

---

### Requirement: OfficialSite constructor

The entity package SHALL provide `NewOfficialSite(artistID, url string) *OfficialSite` that creates an OfficialSite with an auto-generated UUIDv7 ID.

#### Scenario: Constructor generates ID

- **WHEN** NewOfficialSite("artist-123", "https://example.com") is called
- **THEN** returned OfficialSite has non-empty ID, ArtistID="artist-123", URL="https://example.com"

#### Scenario: ID is unique per call

- **WHEN** NewOfficialSite is called twice with the same arguments
- **THEN** each call returns a different ID

---

### Requirement: LogoColorProfile Proto Message
The system SHALL define a `LogoColorProfile` protobuf message within `liverty_music.entity.v1` containing `dominant_hue` (optional float, 0-360, present only for chromatic logos), `dominant_lightness` (float, 0-1), and `is_chromatic` (bool). The `Fanart` message SHALL include an `optional LogoColorProfile logo_color_profile` field.

#### Scenario: Artist with logo analysis data
- **WHEN** an Artist with logo analysis is serialized to proto
- **THEN** the `fanart.logo_color_profile` field SHALL contain a `LogoColorProfile` message with the extracted values

#### Scenario: Artist without logo analysis data
- **WHEN** an Artist without logo analysis is serialized to proto
- **THEN** the `fanart.logo_color_profile` field SHALL be absent (optional not set)
