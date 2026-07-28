## MODIFIED Requirements

### Requirement: Bubble pool cap and eviction on tap
The system SHALL enforce the 50-bubble cap at **both** the pool layer (`BubblePool`) and the physics engine (`BubblePhysics`). The physics engine SHALL never hold more than 50 active bodies at any time, regardless of the code path that triggered the addition.

#### Scenario: Physics engine enforces the cap on addBubbles
- **WHEN** `addBubbles` is called with one or more artists
- **AND** the physics engine already holds 50 or more bodies
- **THEN** the physics engine SHALL add no further bodies
- **AND** it SHALL NOT throw — excess entries are silently skipped

#### Scenario: Stale bodies removed on artist set replacement
- **WHEN** the canvas receives a new set of real (non-ghost) artists via `artistsChanged`
- **AND** the physics engine already holds bodies from a previous artist set
- **THEN** bodies whose artist ID is not present in the new set SHALL be faded out and removed from the physics engine
- **AND** only after stale bodies are scheduled for removal SHALL the new artists be added
- **AND** the total active body count SHALL remain within the 50-bubble cap throughout the transition
