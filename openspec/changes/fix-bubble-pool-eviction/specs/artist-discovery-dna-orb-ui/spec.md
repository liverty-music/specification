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
