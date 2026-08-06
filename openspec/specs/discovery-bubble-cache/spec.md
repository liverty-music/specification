# discovery-bubble-cache Specification

## Purpose
TBD - created by archiving change discovery-bubble-cache. Update Purpose after archive.
## Requirements
### Requirement: Discovery bubble pool is cached in ArtistStore singleton
`ArtistStore` SHALL cache the last successfully generated bubble pool (`Artist[]`) so that `DiscoveryRoute` re-entries can paint real artists immediately without waiting on network RPCs.

#### Scenario: Re-entry paints cached artists instantly
- **WHEN** the user navigates to Discovery after a prior visit
- **AND** at least one cached artist is not yet followed
- **THEN** the bubble pool SHALL be initialized from the filtered cached artists synchronously during `loading()`
- **AND** followed artists SHALL be excluded from the cached pool before it is applied
- **AND** no ghost bubbles SHALL be shown
- **AND** `loadInitialBubbles()` SHALL run in the background to refresh the pool

#### Scenario: Re-entry with all cached artists already followed
- **WHEN** the user navigates to Discovery after a prior visit
- **AND** every artist in the cached pool has since been followed
- **THEN** `pool.replace([])` SHALL be called with an empty array (no stale bubbles rendered)
- **AND** `loadInitialBubbles()` SHALL run immediately in the background and replace the empty pool with fresh artists
- **AND** the bubble field SHALL remain empty until `loadInitialBubbles()` completes (ghost placeholder bubbles are NOT shown on the cached-but-filtered path, unlike a cold visit)

#### Scenario: Cache excludes followed artists on re-entry
- **WHEN** the cached bubble pool contains artists that the user has since followed
- **THEN** those artists SHALL be filtered out before `pool.replace()` is called
- **AND** the followed artists SHALL NOT appear as bubbles in the physics engine

#### Scenario: Cold visit uses ghost bubbles
- **WHEN** no cached artists exist (first visit or cache cleared)
- **THEN** the route SHALL initialize with ghost placeholder bubbles as the current behavior
- **AND** switch to real artists when `loadInitialBubbles()` completes

#### Scenario: Cache is updated after each successful load
- **WHEN** `loadInitialBubbles()` completes successfully
- **THEN** `ArtistStore.setBubbles(pool.availableBubbles)` SHALL be called to persist the pool
- **AND** the next re-entry SHALL use the updated pool

