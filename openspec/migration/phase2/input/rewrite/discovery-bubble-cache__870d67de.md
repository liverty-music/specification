<!-- spec: discovery-bubble-cache | target: components/infrastructure/fan/web/route/discovery | flags: CLASSNAME | new_name: Discovery bubble pool caching on re-entry -->

### Requirement: Discovery bubble pool is cached in ArtistStore singleton
The system SHALL cache the last successfully generated bubble field (`Artist[]`) in a single app-lifetime store so that `DiscoveryRoute` re-entries can paint real artists immediately without waiting on network RPCs. There SHALL be exactly one authoritative bubble-field cache; the raw `listTop` SWR cache and the display-field cache SHALL NOT be maintained as two independent snapshots of the same field.

#### Scenario: Re-entry paints cached artists instantly
- **WHEN** the user navigates to Discovery after a prior visit
- **AND** at least one cached artist is not yet followed
- **THEN** the bubble field SHALL be initialized from the cached field synchronously during `loading()`
- **AND** followed artists SHALL be excluded as part of producing the field
- **AND** no ghost bubbles SHALL be shown
- **AND** any background refresh SHALL reconcile the field via a non-destructive delta (see "Re-entry preserves the in-session bubble field"), NOT a wholesale replacement that recomposes or shrinks the visible field

#### Scenario: Re-entry with all cached artists already followed
- **WHEN** the user navigates to Discovery after a prior visit
- **AND** every artist in the cached field has since been followed
- **THEN** producing the field SHALL exclude all of them, leaving the field empty (no stale bubbles rendered)
- **AND** the background refresh SHALL run immediately and refill the field with fresh artists
- **AND** the field SHALL remain empty until the refresh completes (ghost placeholder bubbles are NOT shown on the cached-but-filtered path, unlike a cold visit)

#### Scenario: Cache excludes followed artists on re-entry
- **WHEN** the cached bubble field contains artists that the user has since followed
- **THEN** those artists SHALL be excluded when the field is produced
- **AND** the followed artists SHALL NOT appear as bubbles in the physics engine

#### Scenario: Cold visit uses ghost bubbles
- **WHEN** no cached field exists (first visit or cache cleared)
- **THEN** the route SHALL initialize with ghost placeholder bubbles as the current behavior
- **AND** switch to real artists when the initial load completes

#### Scenario: Cache is updated after each successful load
- **WHEN** an initial load or refresh completes successfully
- **THEN** the resulting field SHALL be persisted to the single bubble-field cache
- **AND** the next re-entry SHALL use the updated field
