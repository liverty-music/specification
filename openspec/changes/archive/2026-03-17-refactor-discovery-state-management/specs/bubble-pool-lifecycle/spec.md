## MODIFIED Requirements

### Requirement: Bubble pool cap and eviction on tap
The system SHALL maintain a maximum pool size of 50 bubbles, evicting oldest entries when new ones are added. Pool mutations SHALL be coordinated through BubbleManager to ensure physics synchronization.

#### Scenario: Adding similar artists within capacity
- **WHEN** the user taps a bubble and similar artists are fetched
- **AND** the current pool size plus new artists does not exceed 50
- **THEN** the BubbleManager SHALL add all new artists to both pool and physics
- **AND** no existing bubbles SHALL be evicted

#### Scenario: Adding similar artists exceeding capacity
- **WHEN** the user taps a bubble and similar artists are fetched
- **AND** the current pool size plus new artists exceeds 50
- **THEN** the BubbleManager SHALL evict the oldest bubbles first (FIFO)
- **AND** evicted bubbles SHALL be faded out via physics animation before removal from pool
- **AND** new bubbles SHALL be spawned from the tapped bubble's position in both pool and physics

### Requirement: Tap-to-refill flow
The system SHALL fetch similar artists on each bubble tap and manage the pool lifecycle through BubbleManager.

#### Scenario: Successful tap and refill (Steps 3-4)
- **WHEN** a user taps an artist bubble
- **THEN** the system SHALL follow the tapped artist via FollowOrchestrator
- **AND** the system SHALL call `ArtistService.ListSimilar` with `limit=30` for the tapped artist
- **AND** the BubbleManager SHALL add deduplicated results via the coordinated eviction mechanism
- **AND** the cycle SHALL repeat for subsequent taps (Step 6)

#### Scenario: No similar artists found
- **WHEN** the `ListSimilar` response returns zero artists
- **THEN** the BubbleManager SHALL NOT evict any existing bubbles
- **AND** the system SHALL display an informational toast notification to the user

#### Scenario: ListSimilar RPC failure
- **WHEN** the `ListSimilar` call fails
- **THEN** the BubbleManager SHALL NOT evict any existing bubbles
- **AND** the system SHALL display a warning toast notification to the user
