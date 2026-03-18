## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: Internal follow tracking in BubblePool

**Reason**: Follow state management is moving to FollowOrchestrator as the single source of truth. BubblePool's internal `followedIds` Set, `markFollowed()`, `unmarkFollowed()`, and `isFollowed()` create a second data structure that must be manually synchronized with FollowOrchestrator's `followedArtists` array.

**Migration**: Remove `followedIds` Set, `markFollowed()`, `unmarkFollowed()`, `isFollowed()` from BubblePool. All callers that called `pool.markFollowed(id)` SHALL instead update `FollowOrchestrator.followedArtists` and call `pool.remove(id)` separately. All callers that called `pool.isFollowed(id)` SHALL instead check `FollowOrchestrator.followedIds.has(id)`. The `dedup()` method SHALL accept `followedIds` as a parameter. The `reset()` method SHALL no longer clear follow state.
