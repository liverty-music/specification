<!-- spec: artist-image | target: components/usecase/artist/sync-artist-image | flags: CLASSNAME | new_name: Artist image sync resolves found/absent/unavailable outcomes -->

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
