<!-- spec: bubble-state-management | target: components/infrastructure/fan/web/route/discovery | flags: CLASSNAME | new_name: Bubble field reset restores global top artists -->

### Requirement: Bubble field reset restores global top artists
The system SHALL provide a reset operation that discards the current bubble field and re-seeds it with the global top artists, keeping pool state and physics state synchronized. The reset SHALL be independent of the user's followed artists and SHALL NOT use the follow-seeded similar-artist path.

#### Scenario: Reset replaces the pool with global top artists
- **WHEN** the reset operation is invoked
- **THEN** the system SHALL fetch the global top artists for the user's country with no genre filter, up to 50 artists
- **AND** SHALL exclude followed artists from the result
- **AND** SHALL replace the entire pool with the deduplicated result capped at the 50-bubble limit

#### Scenario: Reset clears accumulated discovery state
- **WHEN** the reset operation is invoked after similar-artist bubbles have accumulated
- **THEN** the system SHALL clear the deduplication seen-sets and re-track only the newly seeded artists
- **AND** SHALL discard prior eviction history so the new field is a clean baseline

#### Scenario: Reset re-synchronizes physics state
- **WHEN** the reset operation completes
- **THEN** the canvas SHALL be reloaded so the rendered physics bodies match the new pool
- **AND** the pool count and physics body count SHALL be equal after reset completes
