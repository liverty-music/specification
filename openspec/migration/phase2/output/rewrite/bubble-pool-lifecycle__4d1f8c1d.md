<!-- spec: bubble-pool-lifecycle | target: components/infrastructure/fan/web/route/discovery | flags: CLASSNAME | new_name: Bubble pool initialization based on followed-artist count -->

### Requirement: Bubble pool initialization based on followed-artist count
The system SHALL initialize the bubble pool differently based on whether the user follows any artists. On page load, the system SHALL hydrate the follow state from the persisted store before initializing the pool.

#### Scenario: No followed artists (Step 1-a)
- **WHEN** the discovery page loads
- **AND** the user follows zero artists (including after checking persisted guest state)
- **THEN** the system SHALL detect the user's country via browser timezone detection
- **AND** the system SHALL call `ArtistService.ListTop` with `limit=50` and the detected country
- **AND** if country detection returns empty, the system SHALL pass an empty country (global chart fallback)
- **AND** the system SHALL populate the bubble pool with the response artists

#### Scenario: User has followed artists (Step 1-b)
- **WHEN** the discovery page loads
- **AND** the user follows one or more artists (including artists restored from persisted guest state)
- **THEN** the system SHALL randomly select up to 5 followed artists as seeds
- **AND** the system SHALL call `ArtistService.ListSimilar` for each seed in parallel with the limit evenly distributed to fill 50 total (e.g., 5 seeds × limit=10, 2 seeds × limit=25)

#### Scenario: Seed selection with fewer than 5 followed artists
- **WHEN** the user follows fewer than 5 artists
- **THEN** the system SHALL use all followed artists as seeds
- **AND** the limit per seed SHALL be `floor(50 / followedCount)`

#### Scenario: Follow state hydration on page reload
- **WHEN** the discovery page loads during onboarding
- **AND** previously followed artists exist in persisted guest storage
- **THEN** the system SHALL restore the followed-artist state from persisted storage before initializing the bubble pool
- **AND** the restored followed-artist IDs SHALL be used for deduplication when loading the initial bubble pool
- **AND** the restored followed artists SHALL be passed as input when initializing the bubble pool
