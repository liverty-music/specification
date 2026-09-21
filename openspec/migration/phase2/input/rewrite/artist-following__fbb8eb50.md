<!-- spec: artist-following | target: components/infrastructure/fan/web/global/artist-filter-bar | flags: CLASSNAME | new_name: Filter sheet initializes selection from followed artists -->

### Requirement: ArtistFilterBar sheet initializes pendingIds from followedArtists

When the ArtistFilterBar sheet is opened, it SHALL initialize its `pendingIds` state from the current `followedArtists` observable so that the selection reflects the user's actual followed artists.

#### Scenario: Empty followedArtists on openSheet

- **GIVEN** the `followedArtists` observable is empty
- **WHEN** `openSheet` is called
- **THEN** `pendingIds` SHALL be initialized to an empty set

#### Scenario: Multiple followed artists on openSheet

- **GIVEN** the `followedArtists` observable contains multiple artists
- **WHEN** `openSheet` is called
- **THEN** `pendingIds` SHALL be initialized with the IDs of all currently followed artists

#### Scenario: openSheet called twice resets pendingIds

- **GIVEN** the sheet has been opened and `pendingIds` has been mutated
- **WHEN** `openSheet` is called again
- **THEN** `pendingIds` SHALL be reset to reflect the current `followedArtists` observable, discarding any prior mutations
