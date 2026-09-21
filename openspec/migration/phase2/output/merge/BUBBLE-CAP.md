<!-- merge_group: BUBBLE-CAP | target: components/infrastructure/fan/web/route/discovery | members: 2 -->
<!-- renamed_scenarios: 0 -->

### Requirement: Bubble Field Consistency and Capacity Enforcement

The discovery page SHALL manage the current display field (`Artist[]`) as the
single source of truth for which artist bubbles are shown, and every other
representation — the physics bodies, any cache — SHALL be a derived
projection of that field. Pool state and physics state SHALL be synchronized
such that the rendered physics-body count equals the field count at rest,
including after a background refresh replaces the field. No representation
other than the field SHALL hold authoritative membership. The discovery page
SHALL enforce a 50-bubble capacity limit by coordinating pool eviction with
physics fade-out in a single atomic operation.

#### Scenario: Adding bubbles synchronizes pool and physics
- **WHEN** new artist bubbles are added to the field
- **THEN** the discovery page SHALL update the field AND the physics projection SHALL reconcile to it
- **AND** the field count and physics body count SHALL be equal after the operation

#### Scenario: Removing a bubble synchronizes pool and physics
- **WHEN** an artist bubble is removed from the field (e.g., followed)
- **THEN** the discovery page SHALL remove it from the field AND the physics projection SHALL remove the body
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

#### Scenario: Adding bubbles within capacity
- **WHEN** new bubbles are added and current count plus new count does not exceed 50
- **THEN** the discovery page SHALL add all new bubbles without eviction

#### Scenario: Adding bubbles exceeding capacity
- **WHEN** new bubbles are added and current count plus new count exceeds 50
- **THEN** the discovery page SHALL first fade out the oldest physics bodies (FIFO)
- **AND** SHALL remove the corresponding pool entries
- **AND** SHALL then add the new bubbles to both pool and physics
- **AND** the total count SHALL NOT exceed 50
