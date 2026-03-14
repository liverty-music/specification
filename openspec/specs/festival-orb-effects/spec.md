# Festival Orb Effects

## ADDED Requirements

### Requirement: Stage-level escalation system
The system SHALL calculate visual effect parameters from the follow count using a stage-level model, where each follow advances the stage by one level. The calculation SHALL be implemented as a pure function in `stage-effects.ts`, separate from rendering logic.

#### Scenario: Stage parameters at zero follows
- **WHEN** the follow count is 0
- **THEN** `getStageParams(0)` SHALL return `orbRadius` of 60, `orbitalCount` of 0, `lightRayCount` of 0, `groundGlowAlpha` of 0, `shockwaveEnabled` as false, and `cometTrailEnabled` as false

#### Scenario: Stage parameters at one follow
- **WHEN** the follow count is 1
- **THEN** `getStageParams(1)` SHALL return `orbRadius` of 68, `breathAmplitude` greater than 0, `orbitalCount` of 0, and `particleVisibilityRatio` greater than 0.3

#### Scenario: Stage parameters at two follows
- **WHEN** the follow count is 2
- **THEN** `getStageParams(2)` SHALL return `orbitalCount` of 2 and `groundGlowAlpha` greater than 0

#### Scenario: Stage parameters at four follows
- **WHEN** the follow count is 4
- **THEN** `getStageParams(4)` SHALL return `lightRayCount` of 2, `cometTrailEnabled` as true, and `orbitalCount` of 6

#### Scenario: Stage parameters at five follows
- **WHEN** the follow count is 5
- **THEN** `getStageParams(5)` SHALL return `shockwaveEnabled` as true and `lightRayCount` of 4

#### Scenario: Stage parameters at six or more follows
- **WHEN** the follow count is 6 or more
- **THEN** `getStageParams` SHALL return `lightRayCount` of 6, `orbitalCount` of 10 or more, and all effect features enabled

#### Scenario: Orb radius growth ceiling
- **WHEN** the follow count exceeds 20
- **THEN** the `orbRadius` SHALL NOT exceed 120

#### Scenario: Stage params are deterministic
- **WHEN** `getStageParams` is called multiple times with the same follow count
- **THEN** it SHALL return identical results each time (pure function, no side effects)

---

### Requirement: Growing orb with dynamic bubble boundary
The orb SHALL grow in radius as the user follows more artists, and the Matter.js physics boundary SHALL move upward to accommodate the larger orb, pushing bubbles into a smaller play area.

#### Scenario: Orb radius increases on follow
- **WHEN** the follow count increases from N to N+1
- **THEN** the orb radius SHALL increase according to the stage params formula
- **AND** the orb SHALL render at the new radius on the next frame

#### Scenario: Matter.js bottom wall repositions
- **WHEN** the orb radius changes
- **THEN** the bottom wall position SHALL update to `canvasHeight - (orbRadius * 2 + 20)`
- **AND** existing bubbles SHALL be pushed upward by the physics engine if they overlap the new wall position

#### Scenario: Bubble area remains usable at maximum orb size
- **WHEN** the orb is at maximum radius (120px)
- **THEN** at least 55% of the canvas height SHALL remain available for bubble physics

---

### Requirement: Breathing pulse animation
The orb SHALL exhibit a continuous breathing animation that increases in amplitude and speed with the stage level.

#### Scenario: Breathing at stage 1+
- **WHEN** the follow count is 1 or more
- **THEN** the orb radius SHALL oscillate using a sinusoidal function
- **AND** the amplitude SHALL be determined by `stageParams.breathAmplitude`
- **AND** the speed SHALL be determined by `stageParams.breathSpeed`

#### Scenario: No breathing at stage 0
- **WHEN** the follow count is 0
- **THEN** the orb radius SHALL remain static (breathAmplitude = 0)

#### Scenario: Breathing respects reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** the breathing animation SHALL be suppressed (amplitude forced to 0)

---

### Requirement: Orbital particles
Glowing particles SHALL orbit outside the orb, with count and speed increasing per stage level.

#### Scenario: Orbital appearance at stage 2
- **WHEN** the follow count reaches 2
- **THEN** 2 orbital particles SHALL appear, circling the orb at a radius between 1.3x and 1.8x the orb radius

#### Scenario: Orbital count increases with stage
- **WHEN** the follow count increases
- **THEN** the visible orbital count SHALL match `stageParams.orbitalCount`
- **AND** new orbitals SHALL use colors from the accumulated color palette

#### Scenario: Orbital rendering
- **WHEN** orbital particles are rendered
- **THEN** each SHALL be drawn as a small radial gradient (glow dot) of 2-5px
- **AND** each SHALL have an independent angular velocity

#### Scenario: Orbitals respect reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** orbital particles SHALL be positioned statically (no rotation)

---

### Requirement: Light rays
Radial light beams SHALL emanate from the orb at higher stage levels, using additive blending.

#### Scenario: Light rays appear at stage 4
- **WHEN** the follow count reaches 4
- **THEN** 2 light rays SHALL appear, rendered as triangular gradients extending from the orb center
- **AND** rays SHALL rotate slowly over time

#### Scenario: Light ray count and intensity scale with stage
- **WHEN** the follow count increases beyond 4
- **THEN** the ray count SHALL increase up to `stageParams.lightRayCount`
- **AND** the ray alpha SHALL increase up to `stageParams.lightRayAlpha`

#### Scenario: Light ray blending
- **WHEN** light rays are rendered
- **THEN** `globalCompositeOperation` SHALL be set to `'screen'` for the ray drawing
- **AND** the composition mode SHALL be restored after ray rendering (via `save`/`restore`)

#### Scenario: Light rays respect reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** light rays SHALL be rendered at a fixed angle (no rotation)

---

### Requirement: Shockwave rings on follow
An expanding colored ring SHALL burst from the orb each time an artist is followed.

#### Scenario: Shockwave spawns on absorption complete
- **WHEN** a bubble absorption animation completes (progress reaches 1.0)
- **AND** `stageParams.shockwaveEnabled` is true
- **THEN** a shockwave ring SHALL spawn at the orb center
- **AND** the ring color SHALL use the absorbed artist's hue

#### Scenario: Shockwave ring animation
- **WHEN** a shockwave ring is active
- **THEN** its radius SHALL expand from `orbRadius` to `orbRadius * 3` over 800ms
- **AND** its alpha SHALL decrease from 0.6 to 0
- **AND** its lineWidth SHALL decrease from 3 to 0.5

#### Scenario: Shockwave ring cleanup
- **WHEN** a shockwave ring's alpha reaches 0
- **THEN** it SHALL be recycled (marked inactive for reuse)
- **AND** at most 3 shockwave rings SHALL be active simultaneously

#### Scenario: Shockwave respects reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** shockwave rings SHALL NOT be spawned

---

### Requirement: Comet trail on absorption
Absorbed bubbles SHALL leave a colored trail along their bezier path.

#### Scenario: Trail point accumulation
- **WHEN** a bubble absorption animation is in progress
- **THEN** the current position SHALL be recorded each frame
- **AND** the system SHALL retain the most recent 12 positions in a circular buffer

#### Scenario: Trail rendering
- **WHEN** the comet trail is rendered
- **THEN** trail points SHALL be connected with line segments
- **AND** line width SHALL decrease from 4px (head) to 1px (tail)
- **AND** opacity SHALL decrease from 0.7 (head) to 0.05 (tail)
- **AND** the trail color SHALL use the artist's hue

#### Scenario: Comet trail gated by stage level
- **WHEN** `stageParams.cometTrailEnabled` is false
- **THEN** trail points SHALL NOT be recorded and no trail SHALL be rendered

---

### Requirement: Ground glow
A soft gradient reflection SHALL appear at the bottom of the canvas, tied to stage level.

#### Scenario: Ground glow appearance
- **WHEN** the follow count reaches 2
- **THEN** a vertical linear gradient SHALL render at the bottom 15% of the canvas
- **AND** the gradient alpha SHALL be `stageParams.groundGlowAlpha`

#### Scenario: Ground glow color matches orb
- **WHEN** the ground glow is rendered
- **THEN** its hue SHALL match the dominant hue of the orb's accumulated color palette

#### Scenario: Ground glow uses additive blending
- **WHEN** the ground glow is rendered
- **THEN** `globalCompositeOperation` SHALL be set to `'screen'`
- **AND** the composition mode SHALL be restored after rendering

---

### Requirement: Color palette accumulation
The orb SHALL accumulate a palette of artist hues as users follow artists, enriching the visual diversity of effects.

#### Scenario: Palette grows on inject
- **WHEN** `injectColor(hue)` is called
- **THEN** the hue SHALL be appended to the color palette array

#### Scenario: Palette cap
- **WHEN** the palette reaches 20 entries
- **THEN** new hues SHALL replace the oldest entry (FIFO)

#### Scenario: Palette colors distributed to effects
- **WHEN** orbital particles or light rays are rendered
- **THEN** their colors SHALL be sampled from the accumulated palette, distributed evenly across entries

---

### Requirement: Unit test coverage for stage effects
The `stage-effects.ts` module SHALL be covered by unit tests verifying parameter correctness at key follow counts.

#### Scenario: Boundary value tests
- **WHEN** unit tests run for `getStageParams`
- **THEN** tests SHALL verify correct parameters at follow counts 0, 1, 2, 3, 4, 5, 6, 10, and 20

#### Scenario: Monotonic growth assertions
- **WHEN** unit tests run
- **THEN** tests SHALL verify that `orbRadius`, `orbitalCount`, `lightRayCount`, and `groundGlowAlpha` are monotonically non-decreasing as follow count increases from 0 to 20

#### Scenario: Ceiling assertions
- **WHEN** unit tests run
- **THEN** tests SHALL verify that `orbRadius` never exceeds 120 and `orbitalCount` never exceeds 12

### Requirement: Unit test coverage for OrbRenderer state
OrbRenderer state transitions SHALL be covered by unit tests.

#### Scenario: Shockwave lifecycle test
- **WHEN** a shockwave is spawned and updated until completion
- **THEN** tests SHALL verify it becomes inactive after 800ms of updates

#### Scenario: Color palette accumulation test
- **WHEN** `injectColor` is called 25 times
- **THEN** the palette SHALL contain exactly 20 entries (FIFO cap)

#### Scenario: Orbital count reflects stage params
- **WHEN** `setFollowCount` is called with increasing values
- **THEN** the visible orbital count SHALL match the corresponding `stageParams.orbitalCount`

### Requirement: Unit test coverage for AbsorptionAnimator comet trail
The comet trail's circular buffer behavior SHALL be covered by unit tests.

#### Scenario: Trail buffer accumulation
- **WHEN** an absorption animation runs for 20 frames
- **THEN** the trail buffer SHALL contain exactly 12 entries (the most recent 12)

#### Scenario: Trail disabled at low stage
- **WHEN** comet trail is disabled via stage params
- **THEN** the trail buffer SHALL remain empty regardless of animation progress
