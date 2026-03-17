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
