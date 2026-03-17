## MODIFIED Requirements

### Requirement: Bubble pool deduplication
The system SHALL remove duplicate and already-followed artists from the bubble pool. Follow state SHALL be provided externally rather than tracked internally by the pool.

#### Scenario: Deduplication on initial load (Step 2)
- **WHEN** the bubble pool is populated from any source
- **THEN** the caller SHALL provide a `followedIds: ReadonlySet<string>` parameter to the dedup method
- **AND** the system SHALL remove artists that match any already-seen artist by name (case-insensitive), internal ID, or MBID
- **AND** the system SHALL remove artists whose ID is in the provided `followedIds` set
- **AND** the system SHALL cap the pool at a maximum of 50 bubbles

#### Scenario: Deduplication after tap refill (Step 5)
- **WHEN** similar artists are added to the pool after a tap
- **THEN** the system SHALL apply the same deduplication rules as Step 2
- **AND** the caller SHALL provide the current `followedIds` from the Store
- **AND** already-seen artists from prior fetches SHALL be excluded

## REMOVED Requirements

### Requirement: Internal follow tracking in BubblePool

**Reason**: Follow state management is moving to `@aurelia/state` Store as the single source of truth. BubblePool's internal `followedIds` Set, `markFollowed()`, `unmarkFollowed()`, and `isFollowed()` are redundant and create dual-state bugs.

**Migration**: Remove `followedIds` Set, `markFollowed()`, `unmarkFollowed()`, `isFollowed()` from BubblePool. All callers that called `pool.markFollowed(id)` SHALL instead dispatch `discovery/follow` to the Store. All callers that called `pool.isFollowed(id)` SHALL instead check Store state. The `dedup()` method SHALL accept `followedIds` as a parameter.
