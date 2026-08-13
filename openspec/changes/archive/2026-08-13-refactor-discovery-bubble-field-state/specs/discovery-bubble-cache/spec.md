## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Re-entry preserves the in-session bubble field
Within a session, navigating away from Discovery and back SHALL preserve the field the user was viewing rather than re-deriving it. When the cached field is fresh (within its TTL), the system SHALL reuse it and apply only a non-destructive delta; it SHALL NOT issue a wholesale `replace()` that recomposes the field or reduces it below the display floor.

#### Scenario: Fresh field is reused on re-entry
- **WHEN** the user returns to Discovery within the cache TTL
- **THEN** the previously displayed field SHALL be reused as the starting field
- **AND** the rendered bubble count SHALL NOT drop below the count shown before leaving, except for artists the user followed while away

#### Scenario: Non-destructive delta on refresh
- **WHEN** a background refresh runs on re-entry
- **THEN** it SHALL remove only newly-followed artists and top up only if the field is below the display floor
- **AND** it SHALL NOT replace the entire field with a freshly-fetched set that changes composition or shrinks the field

#### Scenario: Follow while away is reconciled without collapsing the field
- **WHEN** the user followed one or more artists on another route and returns to Discovery
- **THEN** only the newly-followed artists SHALL be removed from the field
- **AND** the remaining bubbles SHALL stay, with top-up applied only to restore the display floor

#### Scenario: Stale field triggers a full reload
- **WHEN** the user returns to Discovery after the cache TTL has expired
- **THEN** the system MAY perform a full reload as on a cold visit
- **AND** the reload SHALL still converge to a field within capacity with render parity
