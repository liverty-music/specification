<!-- spec: festival-orb-effects | target: components/infrastructure/fan/web/global/dna-orb | flags: CLASSNAME | new_name: Stage-level escalation system -->

### Requirement: Stage-level escalation system
The system SHALL calculate visual effect parameters from the follow count using a stage-level model, where each follow advances the stage by one level. The calculation SHALL be implemented as a pure function in `stage-effects.ts`, separate from rendering logic. Full visual intensity SHALL be reached at follow 5.

#### Scenario: Stage parameters at zero follows
- **WHEN** the follow count is 0
- **THEN** `getStageParams(0)` SHALL return `orbRadius` of 60, `orbitalCount` of 0, `lightRayCount` of 0, `groundGlowAlpha` of 0, `shockwaveEnabled` as false, `cometTrailEnabled` as false, `nebulaLayerCount` of 0, `vortexTrailLength` of 0, `beatBPM` of 0, `strobeEnabled` as false, `orbitalTailArc` of 0, and `orbitalSize` of 2

#### Scenario: Stage parameters at one follow
- **WHEN** the follow count is 1
- **THEN** `getStageParams(1)` SHALL return `orbRadius` of 72, `breathAmplitude` greater than 0, `orbitalCount` of 2, `particleVisibilityRatio` greater than 0.3, `groundGlowAlpha` greater than 0, `vortexTrailLength` of 2, and `orbitalSize` of 4

#### Scenario: Stage parameters at two follows
- **WHEN** the follow count is 2
- **THEN** `getStageParams(2)` SHALL return `orbitalCount` of 5, `lightRayCount` of 2, `nebulaLayerCount` of 1, `beatBPM` greater than 0, and `orbitalTailArc` greater than 0

#### Scenario: Stage parameters at three follows
- **WHEN** the follow count is 3
- **THEN** `getStageParams(3)` SHALL return `shockwaveEnabled` as true, `cometTrailEnabled` as true, `strobeEnabled` as true, `vortexTrailLength` of 6, and `lightRayCount` of 6

#### Scenario: Stage parameters at four follows
- **WHEN** the follow count is 4
- **THEN** `getStageParams(4)` SHALL return `nebulaLayerCount` of 3, `orbitalTailArc` of 45, `orbitalSize` of 8, and `orbitalCount` of 11

#### Scenario: Stage parameters at five follows (full show)
- **WHEN** the follow count is 5
- **THEN** `getStageParams(5)` SHALL return maximum intensity values: `lightRayCount` of 12 or more, `orbitalCount` of 12, `beatBPM` of 2.0, `lightRayAlpha` of 0.35 or more, and all effect features enabled

#### Scenario: Stage parameters at six or more follows
- **WHEN** the follow count is 6 or more
- **THEN** `getStageParams` SHALL return the same maximum intensity values as follow 5 (all effects capped at full show level)

#### Scenario: Orb radius growth ceiling
- **WHEN** the follow count exceeds 20
- **THEN** the `orbRadius` SHALL NOT exceed 120

#### Scenario: Stage params are deterministic
- **WHEN** `getStageParams` is called multiple times with the same follow count
- **THEN** it SHALL return identical results each time (pure function, no side effects)

---
