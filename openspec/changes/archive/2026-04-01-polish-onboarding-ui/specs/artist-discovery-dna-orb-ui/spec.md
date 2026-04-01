## MODIFIED Requirements

### Requirement: Bubble Absorption Animation
The system SHALL provide satisfying visual feedback when users select artists by animating bubbles into the DNA Orb, with accumulating visual intensity and comet trail effects.

#### Scenario: First follow has maximum visual impact
- **WHEN** the user follows their first artist (followCount goes from 0 to 1)
- **THEN** the orb radius SHALL increase from 60 to 67.5
- **AND** the breathing pulse SHALL begin
- **AND** the visible particle count SHALL increase noticeably

#### Scenario: Orb visual evolution with stage-level escalation
- **WHEN** the user follows more artists
- **THEN** the orb's visual presentation SHALL be determined by `getStageParams(followCount)` from `stage-effects.ts`
- **AND** the orb radius SHALL grow from BASE_RADIUS=60 by 7.5 per follow, reaching MAX_RADIUS=90 at 4 follows
- **AND** the orb radius, orbital count, light ray count, breathing amplitude, and ground glow SHALL all be driven by the returned `StageParams`
- **AND** each follow SHALL produce a visibly distinct escalation in effects

#### Scenario: Orb growth curve constants
- **WHEN** `getStageParams(followCount)` computes `orbRadius`
- **THEN** `BASE_RADIUS` SHALL be 60
- **AND** `GROWTH_PER_FOLLOW` SHALL be 7.5
- **AND** `LINEAR_STEPS` SHALL be 4
- **AND** `MAX_RADIUS` SHALL be 90
- **AND** for followCount 0-4, orbRadius SHALL equal `BASE_RADIUS + followCount * GROWTH_PER_FOLLOW`
- **AND** for followCount 5+, orbRadius SHALL use logarithmic tail capped at MAX_RADIUS

#### Scenario: Bubble physics zone height matches orb size
- **WHEN** the bubble physics engine initializes wall boundaries
- **THEN** the orb zone height (bottom wall position) SHALL be 130px
- **AND** this SHALL provide sufficient clearance for the orb at MAX_RADIUS=90 plus glow effects
