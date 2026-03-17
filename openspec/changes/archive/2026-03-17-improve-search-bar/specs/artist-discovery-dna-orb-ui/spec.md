## MODIFIED Requirements

### Requirement: Similar Artist Chain Reaction
The system SHALL generate new artist recommendations dynamically using the backend ArtistService.ListSimilar RPC with a limit parameter. The frontend SHALL call the Follow RPC when a user taps an artist bubble. The fetch SHALL NOT directly mutate the bubble pool — the caller SHALL manage eviction and insertion via `addToPool()`.

#### Scenario: Similar artist bubble spawning
- **WHEN** a user taps an artist bubble
- **THEN** the system SHALL call the backend `ArtistService.ListSimilar` RPC with the selected artist's ID and `limit=30`
- **AND** the system SHALL deduplicate the results (excluding seen and followed artists)
- **AND** the system SHALL add results to the pool via `addToPool()`, evicting oldest bubbles if the pool would exceed 50
- **AND** evicted bubbles SHALL be faded out before new bubbles spawn
- **AND** new bubbles representing similar artists SHALL spawn from the original bubble's position
- **AND** the new bubbles SHALL appear with a "pop" emergence animation
- **AND** the new bubbles SHALL integrate into the physics-based layout

#### Scenario: Follow RPC called on bubble tap
- **WHEN** a user taps an artist bubble
- **THEN** the frontend SHALL call `this.artistClient.follow({ artistId: new ArtistId({ value: artist.id }) })`
- **AND** the call SHALL be non-blocking (fire-and-forget with error logging)
- **AND** the local state SHALL update immediately without waiting for the RPC response

#### Scenario: Similar artist spawning after search follow
- **WHEN** a user follows an artist from the search results and the absorption animation completes
- **THEN** the system SHALL trigger the same similar artist loading as a direct bubble tap
- **AND** new similar artist bubbles SHALL spawn from the orb position

## ADDED Requirements

### Requirement: Search result item is fully tappable
Each search result item SHALL use the entire row as the interactive tap area, replacing the small follow button.

#### Scenario: Full row tap to follow
- **WHEN** the search results list is displayed
- **THEN** each result item row SHALL be tappable across its full width and height
- **AND** tapping anywhere on the row SHALL trigger the follow action for that artist
- **AND** the row SHALL NOT contain a separate follow button or + icon

#### Scenario: Visual affordance for tappable rows
- **WHEN** search result items are displayed
- **THEN** each unfollowed row SHALL display `cursor: pointer` on hover
- **AND** each row SHALL show a background color change on hover/active state
- **AND** the row SHALL have sufficient touch target size (minimum 48px height)

#### Scenario: Followed artist row is visually distinct and non-interactive
- **WHEN** a search result item represents an already-followed artist
- **THEN** the row SHALL display a ✓ (check) icon
- **AND** the row SHALL appear visually muted (reduced opacity or distinct styling)
- **AND** tapping the row SHALL have no effect (no duplicate follow, no animation)

### Requirement: Spawn and absorb API on canvas
The `DnaOrbCanvas` component SHALL expose a `spawnAndAbsorb` method that combines spawning a temporary bubble and immediately starting its absorption animation.

#### Scenario: spawnAndAbsorb creates and absorbs a bubble
- **WHEN** `spawnAndAbsorb(artist, x, y)` is called
- **THEN** the canvas SHALL start the absorption animation from (x, y) toward the orb center
- **AND** on completion, the canvas SHALL call `orbRenderer.injectColor()` with the artist's hue
- **AND** the canvas SHALL dispatch the `need-more-bubbles` custom event to trigger similar artist loading
