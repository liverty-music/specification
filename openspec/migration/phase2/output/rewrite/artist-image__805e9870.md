<!-- spec: artist-image | target: components/usecase/artist/sync-artist-image | flags: CLASSNAME | new_name: Artist image sync resolves found/absent/unavailable outcomes -->

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
