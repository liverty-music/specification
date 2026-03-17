### Requirement: Event Card Logo Display
The dashboard event card SHALL display the artist's transparent logo image instead of the text artist name when a logo URL is available. The system SHALL use `hd_music_logo` as the primary source and fall back to `music_logo` when `hd_music_logo` is unavailable. When neither logo is available, the card SHALL display the existing text artist name.

#### Scenario: Artist has hd_music_logo
- **WHEN** an event card renders for an artist with `hd_music_logo` in their fanart data
- **THEN** the card SHALL display the `hd_music_logo` image with `object-fit: contain` instead of the text name

#### Scenario: Artist has only music_logo
- **WHEN** an event card renders for an artist with `music_logo` but no `hd_music_logo`
- **THEN** the card SHALL display the `music_logo` image as fallback

#### Scenario: Artist has no logo
- **WHEN** an event card renders for an artist without any logo in their fanart data
- **THEN** the card SHALL display the existing text artist name with the current styling

#### Scenario: Logo image fails to load
- **WHEN** the logo image URL returns an error or times out
- **THEN** the card SHALL fall back to displaying the text artist name

### Requirement: Event Detail Sheet Hero Image
The event detail sheet SHALL display the artist's background image as a hero section above the existing artist header when `artist_background` is available. The hero image SHALL NOT be displayed when no background image exists, preserving the current layout.

#### Scenario: Artist has background image
- **WHEN** the detail sheet opens for an event whose artist has `artist_background` in their fanart data
- **THEN** the sheet SHALL display the background image in a hero section above the artist header with `aspect-ratio: 16/9` and `object-fit: cover`

#### Scenario: Artist has no background image
- **WHEN** the detail sheet opens for an event whose artist has no `artist_background`
- **THEN** the sheet SHALL render the existing layout without a hero section

#### Scenario: Hero image with gradient fade
- **WHEN** the hero image is displayed
- **THEN** the bottom edge of the hero section SHALL fade into the sheet background color via a gradient overlay to ensure visual continuity

### Requirement: Fanart Data Propagation
The frontend service layer SHALL extract fanart image URLs from the `Artist.fanart` proto field in `ListFollowed` responses and propagate them to the `LiveEvent` and `FollowedArtist` view models for consumption by UI components.

#### Scenario: ListFollowed returns artist with fanart
- **WHEN** the `ListFollowed` RPC returns an artist with populated fanart data
- **THEN** the service layer SHALL map `hd_music_logo`, `music_logo`, `artist_background`, and `artist_thumb` URLs to the corresponding view model fields

#### Scenario: ListFollowed returns artist without fanart
- **WHEN** the `ListFollowed` RPC returns an artist without fanart data
- **THEN** the view model image URL fields SHALL be undefined or empty, triggering fallback display in UI components

#### Scenario: Dashboard events enriched with fanart
- **WHEN** the dashboard constructs `LiveEvent` objects from concert data
- **THEN** the system SHALL look up fanart URLs by artist ID from the `ListFollowed` response and attach them to the `LiveEvent`
