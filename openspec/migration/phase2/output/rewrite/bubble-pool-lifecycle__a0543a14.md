<!-- spec: bubble-pool-lifecycle | target: components/infrastructure/fan/web/route/discovery | flags: CLASSNAME | new_name: Tap-to-refill flow -->

### Requirement: Tap-to-refill flow
The system SHALL fetch similar artists on each bubble tap and manage the bubble pool's lifecycle accordingly.

#### Scenario: Successful tap and refill (Steps 3-4)
- **WHEN** a user taps an artist bubble
- **THEN** the system SHALL follow the tapped artist
- **AND** the system SHALL call `ArtistService.ListSimilar` with `limit=30` for the tapped artist
- **AND** the system SHALL add deduplicated results to the pool via the coordinated eviction mechanism
- **AND** the cycle SHALL repeat for subsequent taps (Step 6)

#### Scenario: No similar artists found
- **WHEN** the `ListSimilar` response returns zero artists
- **THEN** the system SHALL NOT evict any existing bubbles
- **AND** the system SHALL display an informational toast notification to the user

#### Scenario: ListSimilar RPC failure
- **WHEN** the `ListSimilar` call fails
- **THEN** the system SHALL NOT evict any existing bubbles
- **AND** the system SHALL display a warning toast notification to the user
