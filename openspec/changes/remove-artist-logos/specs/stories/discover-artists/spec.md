## MODIFIED Requirements

### Requirement: A discovered artist is registered and enriched
When ArtistUseCase.Search, ArtistUseCase.ListTop or ArtistUseCase.ListSimilar returns an artist that was not registered before, the artist SHALL be registered at once and announced as created; the announcement SHALL run ArtistNameResolutionUseCase.ResolveCanonicalName and ArtistImageSyncUseCase.SyncArtistImage for it, so that the artist then carries the catalog's canonical name and its images.

#### Scenario: Newly discovered artist
- **WHEN** a fan searches for a name and a result was not registered before
- **THEN** the result is returned as a registered artist, and after the announcement is handled the artist has the catalog's canonical name and its images

#### Scenario: Already registered artist
- **WHEN** a chart lists an artist that is already registered
- **THEN** the registered artist is returned and no announcement is made for it
