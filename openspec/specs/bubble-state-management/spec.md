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
The system SHALL manage the current display field (`Artist[]`) through a single owner (the BubbleManager / field state), and every other representation — the physics bodies, any cache — SHALL be a derived projection of that field. Pool state and physics state SHALL be synchronized such that the rendered physics-body count equals the field count at rest, including after a background refresh replaces the field. No representation other than the field owner SHALL hold authoritative membership.

#### Scenario: Adding bubbles synchronizes pool and physics
- **WHEN** new artist bubbles are added to the field
- **THEN** the BubbleManager SHALL update the field AND the physics projection SHALL reconcile to it
- **AND** the field count and physics body count SHALL be equal after the operation

#### Scenario: Removing a bubble synchronizes pool and physics
- **WHEN** an artist bubble is removed from the field (e.g., followed)
- **THEN** the BubbleManager SHALL remove it from the field AND the physics projection SHALL remove the body
- **AND** no orphaned physics bodies SHALL remain

#### Scenario: Eviction synchronizes pool and physics
- **WHEN** the field owner evicts oldest bubbles to make room for new ones
- **THEN** the evicted physics bodies SHALL fade out
- **AND** the evicted artists SHALL be removed from the field
- **AND** the field and physics counts SHALL remain equal after eviction completes

#### Scenario: Background refresh preserves render parity
- **WHEN** a background load produces a new field that differs from the currently rendered set
- **THEN** the physics projection SHALL converge to exactly the new field
- **AND** the rendered body count SHALL equal the new field count at rest
- **AND** no field member SHALL be dropped from rendering because fading-out bodies temporarily occupied capacity

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

### Requirement: Physics layer is a pure projection of the field
The physics/canvas layer SHALL render the field it is given and SHALL NOT own bubble policy. It SHALL NOT apply the capacity cap, deduplication, or followed-artist exclusion; those are guaranteed upstream by the field owner. The physics layer SHALL expose a reconcile operation that diffs its current bodies against a target `Artist[]` and applies only the additions and removals needed to match it.

#### Scenario: Reconcile to a target list
- **WHEN** the physics layer is asked to reconcile to a target field
- **THEN** it SHALL keep bodies whose artist is still in the target, remove bodies no longer in the target, and add bodies for new artists in the target
- **AND** the resulting body set SHALL equal the target

#### Scenario: Fading-out bodies do not block replacements
- **WHEN** bodies are fading out while new artists are being added in the same reconcile
- **THEN** the fading-out bodies SHALL NOT count against capacity such that new artists are dropped
- **AND** every artist in the target SHALL receive a body

#### Scenario: Physics never silently drops a target member
- **WHEN** a reconcile target is applied
- **THEN** the physics layer SHALL NOT silently discard any target artist due to a capacity check
- **AND** if a hard safety cap is ever hit, it SHALL be logged rather than dropped silently

### Requirement: Bubble invariants are applied once at the field boundary
The invariants — exclude followed artists, deduplicate by name/id/mbid, and enforce the 50-bubble capacity — SHALL be applied exactly once, when the field owner produces or updates the field. Downstream consumers (router hooks, genre/reset/search flows, the physics layer) SHALL NOT re-apply these invariants independently.

#### Scenario: Followed exclusion happens once
- **WHEN** the field is produced or updated from any source (initial load, cache re-entry, genre, reset, similar top-up)
- **THEN** followed-artist exclusion SHALL be applied by the field owner as part of producing the field
- **AND** no consumer SHALL re-filter followed artists after the field is produced

#### Scenario: Capacity enforced once
- **WHEN** the field is produced or updated
- **THEN** the 50-bubble capacity SHALL be enforced by the field owner
- **AND** the physics layer SHALL receive a field already within capacity and SHALL NOT re-cap it

