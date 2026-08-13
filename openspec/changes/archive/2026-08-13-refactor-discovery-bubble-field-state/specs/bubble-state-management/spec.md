## MODIFIED Requirements

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

## ADDED Requirements

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
