## MODIFIED Requirements

### Requirement: Similar Artist Chain Reaction
The system SHALL generate new artist recommendations dynamically using the backend ArtistService.ListSimilar RPC. The frontend SHALL call the Follow RPC when a user taps an artist bubble.

#### Scenario: Similar artist bubble spawning
- **WHEN** a user taps an artist bubble
- **THEN** the system SHALL call the backend `ArtistService.ListSimilar` RPC with the selected artist's ID
- **AND** new bubbles representing similar artists SHALL spawn from the original bubble's position
- **AND** the new bubbles SHALL appear with a "pop" emergence animation
- **AND** the new bubbles SHALL integrate into the physics-based layout

#### Scenario: Follow RPC called on bubble tap
- **WHEN** a user taps an artist bubble
- **THEN** the frontend SHALL call `this.artistClient.follow({ artistId: new ArtistId({ value: artist.id }) })`
- **AND** the call SHALL be non-blocking (fire-and-forget with error logging)
- **AND** the local state SHALL update immediately without waiting for the RPC response
