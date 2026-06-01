# Bubble State Management

## Purpose

Defines the BubbleManager as the single source of truth for bubble lifecycle, ensuring pool state and physics state are always synchronized. Covers coordinated eviction, capacity enforcement, and safe canvas dimension reads.

**Key Aspects:**
- Unified BubbleManager for pool membership, physics bodies, deduplication, and capacity
- Synchronized pool and physics state on add, remove, and evict operations
- 50-bubble capacity with coordinated FIFO eviction and physics fade-out
- Deferred canvas reads when element is hidden

---
## Requirements
### Requirement: BubbleManager provides single source of truth for bubble lifecycle
The system SHALL manage all bubble state (pool membership, physics bodies, deduplication, capacity) through a unified BubbleManager, ensuring that pool state and physics state are always synchronized.

#### Scenario: Adding bubbles synchronizes pool and physics
- **WHEN** new artist bubbles are added to the BubbleManager
- **THEN** the BubbleManager SHALL add them to the pool AND spawn corresponding physics bodies
- **AND** the pool count and physics body count SHALL be equal after the operation

#### Scenario: Removing a bubble synchronizes pool and physics
- **WHEN** an artist bubble is removed from the BubbleManager (e.g., followed)
- **THEN** the BubbleManager SHALL remove it from the pool AND remove the physics body
- **AND** no orphaned physics bodies SHALL remain

#### Scenario: Eviction synchronizes pool and physics
- **WHEN** the BubbleManager evicts oldest bubbles to make room for new ones
- **THEN** the BubbleManager SHALL fade out the evicted physics bodies
- **AND** SHALL remove the evicted artists from the pool
- **AND** the pool and physics counts SHALL remain equal after eviction completes

### Requirement: BubbleManager enforces capacity through coordinated eviction
The system SHALL enforce the 50-bubble capacity limit by coordinating pool eviction with physics fade-out in a single atomic operation.

#### Scenario: Adding bubbles within capacity
- **WHEN** new bubbles are added and current count plus new count does not exceed 50
- **THEN** the BubbleManager SHALL add all new bubbles without eviction

#### Scenario: Adding bubbles exceeding capacity
- **WHEN** new bubbles are added and current count plus new count exceeds 50
- **THEN** the BubbleManager SHALL first fade out the oldest physics bodies (FIFO)
- **AND** SHALL remove the corresponding pool entries
- **AND** SHALL then add the new bubbles to both pool and physics
- **AND** the total count SHALL NOT exceed 50

### Requirement: BubbleManager defers canvas reads until element is visible
The system SHALL NOT read canvas dimensions while the canvas element has `display: none` or zero-size layout.

#### Scenario: Canvas rect read when visible
- **WHEN** the BubbleManager needs canvas dimensions and the canvas element is visible
- **THEN** the system SHALL return accurate width and height values

#### Scenario: Canvas rect read when hidden
- **WHEN** the BubbleManager needs canvas dimensions and the canvas element is hidden (e.g., during search mode)
- **THEN** the system SHALL defer the read until the element becomes visible (via `requestAnimationFrame`)
- **AND** SHALL NOT spawn bubbles at position (0, 0)

### Requirement: BubbleManager supports reset to global top artists
The BubbleManager SHALL provide a reset operation that discards the current bubble field and re-seeds it with the global top artists, keeping pool state and physics state synchronized. The reset SHALL be independent of the user's followed artists and SHALL NOT use the follow-seeded similar-artist path.

#### Scenario: Reset replaces the pool with global top artists
- **WHEN** the reset operation is invoked
- **THEN** the BubbleManager SHALL fetch the global top artists via `listTop(country, '', 50)`
- **AND** SHALL exclude followed artists from the result
- **AND** SHALL replace the entire pool with the deduplicated result capped at the 50-bubble limit

#### Scenario: Reset clears accumulated discovery state
- **WHEN** the reset operation is invoked after similar-artist bubbles have accumulated
- **THEN** the BubbleManager SHALL clear the deduplication seen-sets and re-track only the newly seeded artists
- **AND** SHALL discard prior eviction history so the new field is a clean baseline

#### Scenario: Reset re-synchronizes physics state
- **WHEN** the reset operation completes
- **THEN** the canvas SHALL be reloaded so the rendered physics bodies match the new pool
- **AND** the pool count and physics body count SHALL be equal after reset completes

### Requirement: Initial load tops up a sparse discovery field
When the user already follows artists, the initial load seeds bubbles from those artists' similar artists. Because the similar lists shrink as follow count grows (seeds are capped, the per-seed limit shrinks, and deduplication removes followed and overlapping artists), the BubbleManager SHALL top up the field with global top artists whenever the deduplicated seed-similar results fall below a minimum target. Similar artists SHALL keep priority. This guarantees the field is never empty and stays reasonably full regardless of how many artists the user follows.

#### Scenario: Sparse seed-similar results are topped up
- **WHEN** the initial load takes the similar-seed path and the deduplicated similar results are below the minimum target
- **THEN** the BubbleManager SHALL append global top artists (deduplicated against followed and already-included artists) up to the bubble cap
- **AND** the similar artists SHALL retain priority order ahead of the top-artist fillers

#### Scenario: Empty seed-similar still fills the field
- **WHEN** the similar lookups resolve to nothing (no matches, errors, or all results deduped away)
- **THEN** the BubbleManager SHALL fill the field with global top artists rather than leaving it empty

#### Scenario: Sufficient seed-similar results are not diluted
- **WHEN** the deduplicated similar results meet or exceed the minimum target
- **THEN** the BubbleManager SHALL NOT fetch or append top artists

