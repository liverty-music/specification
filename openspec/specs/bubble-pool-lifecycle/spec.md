# Bubble Pool Lifecycle

## Purpose

This capability defines the lifecycle management of the artist bubble pool on the Discovery page. It covers initialization strategies based on user state, deduplication logic, capacity management with FIFO eviction, and the tap-to-refill interaction cycle. The pool is capped at 50 bubbles and refreshes dynamically as users interact with artist bubbles.

**Key Aspects:**
- Dual initialization: ListTop for new users, seed-based ListSimilar for returning users
- Deduplication by name, internal ID, and MBID across all fetch operations
- FIFO eviction when pool exceeds 50 bubbles
- Tap → Follow → Fetch Similar → AddToPool → Repeat cycle

---

## Requirements

### Requirement: Bubble pool initialization based on followed-artist count
The system SHALL initialize the bubble pool differently based on whether the user follows any artists.

#### Scenario: No followed artists (Step 1-a)
- **WHEN** the discovery page loads
- **AND** the user follows zero artists
- **THEN** the system SHALL call `ArtistService.ListTop` with `limit=50` and the user's country
- **AND** the system SHALL populate the bubble pool with the response artists

#### Scenario: User has followed artists (Step 1-b)
- **WHEN** the discovery page loads
- **AND** the user follows one or more artists
- **THEN** the system SHALL randomly select up to 5 followed artists as seeds
- **AND** the system SHALL call `ArtistService.ListSimilar` for each seed in parallel with the limit evenly distributed to fill 50 total (e.g., 5 seeds × limit=10, 2 seeds × limit=25)
- **AND** the system SHALL populate the bubble pool with the combined results

#### Scenario: Seed selection with fewer than 5 followed artists
- **WHEN** the user follows fewer than 5 artists
- **THEN** the system SHALL use all followed artists as seeds
- **AND** the limit per seed SHALL be `floor(50 / followedCount)`

---

### Requirement: Bubble pool deduplication
The system SHALL remove duplicate and already-followed artists from the bubble pool.

#### Scenario: Deduplication on initial load (Step 2)
- **WHEN** the bubble pool is populated from any source
- **THEN** the system SHALL remove artists that match any already-seen artist by name (case-insensitive), internal ID, or MBID
- **AND** the system SHALL remove artists that the user already follows
- **AND** the system SHALL cap the pool at a maximum of 50 bubbles

#### Scenario: Deduplication after tap refill (Step 5)
- **WHEN** similar artists are added to the pool after a tap
- **THEN** the system SHALL apply the same deduplication rules as Step 2
- **AND** already-seen artists from prior fetches SHALL be excluded

---

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

---

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

---

### Requirement: ListSimilar and ListTop limit parameter
The `ArtistService.ListSimilar` and `ArtistService.ListTop` RPCs SHALL accept an optional `limit` parameter to control the maximum number of results.

#### Scenario: Limit parameter provided
- **WHEN** a client sends `ListSimilarRequest` or `ListTopRequest` with `limit > 0`
- **THEN** the server SHALL return at most `limit` artists
- **AND** the limit SHALL be validated as an integer between 0 and 100

#### Scenario: Limit parameter omitted or zero
- **WHEN** a client sends a request with `limit = 0` or omits the field
- **THEN** the server SHALL use its default limit
