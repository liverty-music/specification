## ADDED Requirements

### Requirement: Vortex flow trails inside the orb
Inner particles SHALL draw tapered trails of their recent positions to create a fluid, swirling vortex effect inside the orb.

#### Scenario: Trail buffer accumulation
- **WHEN** the orb animation loop runs with `vortexTrailLength > 0`
- **THEN** each inner particle SHALL store its most recent positions in a ring buffer of length `stageParams.vortexTrailLength`
- **AND** one position SHALL be recorded per `update()` call

#### Scenario: Trail rendering as tapered lines
- **WHEN** inner particles are rendered
- **AND** `vortexTrailLength > 0`
- **THEN** each particle SHALL draw a path connecting its trail positions using `lineTo`
- **AND** the line width SHALL taper from `particleSize * 1.5` at the head to `0.5` at the tail
- **AND** the opacity SHALL decrease from the particle's base opacity at the head to `0.05` at the tail

#### Scenario: Vortex trails appear at follow 1
- **WHEN** the follow count is 1 or more
- **THEN** `stageParams.vortexTrailLength` SHALL be greater than 0
- **AND** at follow 3 or more, `vortexTrailLength` SHALL be at its maximum value of 6

#### Scenario: Vortex trails respect reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** trails SHALL NOT be drawn (particles render as single dots as before)

---

### Requirement: Nebula fill layers
The orb SHALL display rotating radial gradient layers inside its body to fill empty space with colorful nebula-like clouds.

#### Scenario: Nebula layer rendering
- **WHEN** `stageParams.nebulaLayerCount > 0`
- **THEN** the renderer SHALL draw that many radial gradients inside the orb boundary
- **AND** each gradient SHALL use colors sampled from the accumulated `colorPalette`
- **AND** each layer SHALL rotate at a distinct speed (each layer offset by a different angular velocity)
- **AND** layers SHALL be composited using `globalCompositeOperation = 'screen'`

#### Scenario: Nebula layers appear at follow 2
- **WHEN** the follow count is 2
- **THEN** `stageParams.nebulaLayerCount` SHALL be 1
- **AND** at follow 4 or more, `nebulaLayerCount` SHALL be at its maximum value of 3

#### Scenario: Nebula alpha is bounded
- **WHEN** nebula layers are rendered
- **THEN** the combined alpha of all layers SHALL NOT exceed 0.25
- **AND** `stageParams.nebulaAlpha` SHALL control the per-layer alpha

#### Scenario: Nebula uses default color when palette is empty
- **WHEN** nebula layers are rendered and `colorPalette` is empty
- **THEN** layers SHALL use the default hue of 260 (purple)

#### Scenario: Nebula respects reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** nebula layers SHALL render at fixed angles (no rotation) but remain visible

---

### Requirement: Strobe flash on follow
A brief full-canvas flash and rapid shockwave burst SHALL fire when a follow action triggers a pulse.

#### Scenario: White flash overlay
- **WHEN** `pulse()` is called and `stageParams.strobeEnabled` is true
- **THEN** the renderer SHALL draw a full-canvas `fillRect` with `rgba(255, 255, 255, 0.15)` for exactly 1 frame
- **AND** the flash SHALL be cleared on the next frame automatically (no manual cleanup)

#### Scenario: Staggered shockwave burst
- **WHEN** `pulse()` is called and `stageParams.strobeEnabled` is true
- **THEN** the renderer SHALL spawn 2-3 shockwave rings with 50ms stagger between each
- **AND** the shockwave pool size SHALL be at least 5 to accommodate the burst

#### Scenario: Light ray alpha spike
- **WHEN** `pulse()` is called
- **THEN** all light ray alphas SHALL spike to 0.8 and decay back to `stageParams.lightRayAlpha` over 200ms

#### Scenario: Strobe enabled at follow 3
- **WHEN** the follow count is 3 or more
- **THEN** `stageParams.strobeEnabled` SHALL be true

#### Scenario: Strobe respects reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** the white flash and alpha spike SHALL be suppressed
- **AND** shockwaves SHALL also be suppressed (existing behavior)

---

### Requirement: Beat sync pulsation
A shared sinusoidal beat SHALL modulate multiple visual parameters to create a rhythmic, concert-like atmosphere.

#### Scenario: Beat phase calculation
- **WHEN** `stageParams.beatBPM > 0` and reduced motion is not active
- **THEN** the renderer SHALL compute `beatPhase = Math.sin(time * beatBPM * Math.PI / 30)` on each `update()`
- **AND** `beatPhase` SHALL range from -1 to 1

#### Scenario: Beat modulates light rays
- **WHEN** beat sync is active and light rays are rendered
- **THEN** each ray's effective alpha SHALL be `stageParams.lightRayAlpha * (1 + beatPhase * 0.1)`

#### Scenario: Beat modulates orbital glow
- **WHEN** beat sync is active and orbitals are rendered
- **THEN** each orbital's effective size SHALL be `orbitalSize * (1 + beatPhase * 0.1)`

#### Scenario: Beat BPM scales with follow count
- **WHEN** the follow count is 2
- **THEN** `stageParams.beatBPM` SHALL be greater than 0
- **AND** at follow 5, `beatBPM` SHALL be at its maximum value of 2.0

#### Scenario: Beat sync respects reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** `beatPhase` SHALL be fixed at 0 (no pulsation)

---

### Requirement: Orbital comet tails
Orbital particles SHALL display trailing arc segments to create a comet-like appearance.

#### Scenario: Orbital tail rendering
- **WHEN** `stageParams.orbitalTailArc > 0`
- **THEN** each orbital particle SHALL draw an arc segment trailing behind its current angle
- **AND** the arc span SHALL be `stageParams.orbitalTailArc` degrees
- **AND** the arc SHALL use a gradient from the orbital's color at full opacity to transparent

#### Scenario: Orbital tails appear at follow 2
- **WHEN** the follow count is 2
- **THEN** `stageParams.orbitalTailArc` SHALL be greater than 0
- **AND** at follow 4 or more, `orbitalTailArc` SHALL be at its maximum value of 45 degrees

#### Scenario: Orbital size increase
- **WHEN** follow count is 1 or more
- **THEN** `stageParams.orbitalSize` SHALL determine the base orbital dot size
- **AND** the size SHALL range from 4 at follow 1 to 8 at follow 4+
- **AND** the glow radius SHALL be `orbitalSize * 4`

#### Scenario: Orbital tails respect reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** orbital tails SHALL NOT be drawn (orbitals render as static dots)

---

## MODIFIED Requirements

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

### Requirement: Light rays
Radial light beams SHALL emanate from the orb at higher stage levels, using additive blending, per-ray gradient coloring, and randomized beam widths.

#### Scenario: Light rays appear at follow 2
- **WHEN** the follow count reaches 2
- **THEN** 2 light rays SHALL appear, rendered as triangular shapes extending from the orb center
- **AND** rays SHALL rotate over time with some rays rotating counter-clockwise

#### Scenario: Light ray count and intensity scale with stage
- **WHEN** the follow count increases beyond 2
- **THEN** the ray count SHALL increase up to `stageParams.lightRayCount` (maximum 12-16)
- **AND** the ray alpha SHALL increase up to `stageParams.lightRayAlpha` (maximum 0.35-0.4)

#### Scenario: Light ray gradient coloring
- **WHEN** light rays are rendered
- **THEN** each ray SHALL use a `createLinearGradient` from orb center to ray tip
- **AND** the gradient SHALL shift hue by +30 to +60 degrees from root to tip
- **AND** the gradient SHALL fade to transparent at the tip

#### Scenario: Light ray width variation
- **WHEN** light rays are initialized
- **THEN** each ray SHALL have a `halfWidth` randomly assigned between `stageParams.lightRayWidthMin` and `stageParams.lightRayWidthMax`

#### Scenario: Light ray blending
- **WHEN** light rays are rendered
- **THEN** `globalCompositeOperation` SHALL be set to `'screen'` for the ray drawing
- **AND** the composition mode SHALL be restored after ray rendering (via `save`/`restore`)

#### Scenario: Light rays respect reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** light rays SHALL be rendered at a fixed angle (no rotation)

---

### Requirement: Orbital particles
Glowing particles SHALL orbit outside the orb, with count and speed increasing per stage level, enlarged size, and comet-like tails.

#### Scenario: Orbital appearance at follow 1
- **WHEN** the follow count reaches 1
- **THEN** 2 orbital particles SHALL appear, circling the orb at a radius between 1.3x and 1.8x the orb radius

#### Scenario: Orbital count increases with stage
- **WHEN** the follow count increases
- **THEN** the visible orbital count SHALL match `stageParams.orbitalCount`
- **AND** new orbitals SHALL use colors from the accumulated color palette

#### Scenario: Orbital rendering with enlarged size
- **WHEN** orbital particles are rendered
- **THEN** each SHALL be drawn as a radial gradient (glow dot) of `stageParams.orbitalSize` (4-8px)
- **AND** the glow radius SHALL be `orbitalSize * 4`
- **AND** each SHALL have an independent angular velocity

#### Scenario: Orbitals respect reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** orbital particles SHALL be positioned statically (no rotation)

---

### Requirement: Shockwave rings on follow
Expanding colored rings SHALL burst from the orb each time an artist is followed, with support for rapid multi-ring bursts.

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

#### Scenario: Shockwave ring pool size
- **WHEN** the shockwave pool is initialized
- **THEN** at least 5 shockwave ring slots SHALL be available to accommodate staggered bursts

#### Scenario: Shockwave respects reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** shockwave rings SHALL NOT be spawned

---

### Requirement: Unit test coverage for stage effects
The `stage-effects.ts` module SHALL be covered by unit tests verifying parameter correctness at key follow counts, including all new StageParams fields.

#### Scenario: Boundary value tests
- **WHEN** unit tests run for `getStageParams`
- **THEN** tests SHALL verify correct parameters at follow counts 0, 1, 2, 3, 4, 5, 6, 10, and 20
- **AND** tests SHALL verify the new fields: `nebulaLayerCount`, `nebulaAlpha`, `vortexTrailLength`, `beatBPM`, `strobeEnabled`, `orbitalTailArc`, `orbitalSize`, `lightRayWidthMin`, `lightRayWidthMax`

#### Scenario: Monotonic growth assertions
- **WHEN** unit tests run
- **THEN** tests SHALL verify that `orbRadius`, `orbitalCount`, `lightRayCount`, `groundGlowAlpha`, `nebulaLayerCount`, `orbitalTailArc`, `orbitalSize`, and `beatBPM` are monotonically non-decreasing as follow count increases from 0 to 20

#### Scenario: Ceiling assertions
- **WHEN** unit tests run
- **THEN** tests SHALL verify that `orbRadius` never exceeds 120, `orbitalCount` never exceeds 12, `nebulaLayerCount` never exceeds 3, and `nebulaAlpha` never exceeds 0.25

#### Scenario: Full show at follow 5
- **WHEN** unit tests run
- **THEN** tests SHALL verify that `getStageParams(5)` returns maximum intensity values for all effect parameters
- **AND** `getStageParams(6)` SHALL return the same maximum values as `getStageParams(5)` for all capped parameters

### Requirement: Unit test coverage for OrbRenderer state
OrbRenderer state transitions SHALL be covered by unit tests, including new effect state.

#### Scenario: Shockwave lifecycle test
- **WHEN** a shockwave is spawned and updated until completion
- **THEN** tests SHALL verify it becomes inactive after 800ms of updates

#### Scenario: Color palette accumulation test
- **WHEN** `injectColor` is called 25 times
- **THEN** the palette SHALL contain exactly 20 entries (FIFO cap)

#### Scenario: Orbital count reflects stage params
- **WHEN** `setFollowCount` is called with increasing values
- **THEN** the visible orbital count SHALL match the corresponding `stageParams.orbitalCount`

#### Scenario: Shockwave pool accommodates burst
- **WHEN** 5 shockwaves are spawned in rapid succession
- **THEN** all 5 SHALL be active simultaneously
