# discovery-bubble-cache Specification

## Purpose
TBD - created by archiving change discovery-bubble-cache. Update Purpose after archive.
## Requirements
### Requirement: Discovery bubble pool is cached in ArtistStore singleton
`ArtistStore` SHALL cache the last successfully generated bubble pool (`Artist[]`) so that `DiscoveryRoute` re-entries can paint real artists immediately without waiting on network RPCs.

#### Scenario: Re-entry paints cached artists instantly
- **WHEN** the user navigates to Discovery after a prior visit
- **THEN** the bubble pool SHALL be initialized from the cached artists synchronously during `loading()`
- **AND** no ghost bubbles SHALL be shown
- **AND** `loadInitialBubbles()` SHALL run in the background to refresh the pool

#### Scenario: Cold visit uses ghost bubbles
- **WHEN** no cached artists exist (first visit or cache cleared)
- **THEN** the route SHALL initialize with ghost placeholder bubbles as the current behavior
- **AND** switch to real artists when `loadInitialBubbles()` completes

#### Scenario: Cache is updated after each successful load
- **WHEN** `loadInitialBubbles()` completes successfully
- **THEN** `ArtistStore.setBubbles(pool.availableBubbles)` SHALL be called to persist the pool
- **AND** the next re-entry SHALL use the updated pool

