## MODIFIED Requirements

### Requirement: Bubble pool initialization based on followed-artist count

The system SHALL initialize the bubble pool differently based on whether the user follows any artists. On page load, the system SHALL hydrate the follow state from the persisted store before initializing the pool.

#### Scenario: No followed artists (Step 1-a)

- **WHEN** the discovery page loads
- **AND** the user follows zero artists (including after checking persisted guest state)
- **THEN** the system SHALL call `ArtistService.ListTop` with `limit=50` and the user's country
- **AND** the system SHALL populate the bubble pool with the response artists

#### Scenario: User has followed artists (Step 1-b)

- **WHEN** the discovery page loads
- **AND** the user follows one or more artists (including artists restored from persisted guest state)
- **THEN** the system SHALL randomly select up to 5 followed artists as seeds
- **AND** the system SHALL call `ArtistService.ListSimilar` for each seed in parallel with the limit evenly distributed to fill 50 total (e.g., 5 seeds × limit=10, 2 seeds × limit=25)
- **AND** the system SHALL populate the bubble pool with the combined results

#### Scenario: Seed selection with fewer than 5 followed artists

- **WHEN** the user follows fewer than 5 artists
- **THEN** the system SHALL use all followed artists as seeds
- **AND** the limit per seed SHALL be `floor(50 / followedCount)`

#### Scenario: Follow state hydration on page reload

- **WHEN** the discovery page loads during onboarding
- **AND** `guest.followedArtists` exists in localStorage (restored into the store by `loadPersistedState()`)
- **THEN** the system SHALL hydrate `FollowOrchestrator.followedArtists` from `store.getState().guest.follows` before initializing the bubble pool
- **AND** the hydrated `followedIds` SHALL be used for deduplication during `loadInitialArtists()`
- **AND** the hydrated followed artists SHALL be passed to `BubbleManager.loadInitialArtists()` as the `followedArtists` parameter

### Requirement: Bubble pool deduplication

The system SHALL remove duplicate and already-followed artists from the bubble pool. Follow state SHALL be provided externally via a `followedIds` parameter rather than tracked internally by the pool.

#### Scenario: Deduplication on initial load (Step 2)

- **WHEN** the bubble pool is populated from any source
- **THEN** the caller SHALL provide a `followedIds: ReadonlySet<string>` parameter to the dedup method
- **AND** the system SHALL remove artists that match any already-seen artist by name (case-insensitive), internal ID, or MBID
- **AND** the system SHALL remove artists whose ID is in the provided `followedIds` set
- **AND** the system SHALL cap the pool at a maximum of 50 bubbles

#### Scenario: Deduplication after tap refill (Step 5)

- **WHEN** similar artists are added to the pool after a tap
- **THEN** the system SHALL apply the same deduplication rules as Step 2
- **AND** the caller SHALL provide the current `followedIds` derived from the FollowOrchestrator
- **AND** already-seen artists from prior fetches SHALL be excluded

#### Scenario: Deduplication on genre reload

- **WHEN** the genre filter reloads the bubble pool
- **THEN** the caller SHALL provide the current `followedIds` derived from the followed artists list
- **AND** the system SHALL apply the same deduplication rules as Step 2
