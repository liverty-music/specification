# Dna Orb

## Purpose

Provides the central visual orb that grows and accumulates each followed artist's color as the user follows more artists during discovery, animating absorption, follow celebrations, and escalating festival-style effects while respecting reduced-motion preferences.

## Requirements

### Requirement: Bubble Absorption Animation
The system SHALL provide satisfying visual feedback when users select artists by first bursting the tapped bubble in place and then animating its color into the DNA Orb, with accumulating visual intensity and comet trail effects.

#### Scenario: Artist selection bursts then absorbs
- **WHEN** a user taps an artist bubble
- **THEN** the bubble SHALL first play a burst effect at the tap point (see "Bubble Burst On Tap") before the absorption animation begins
- **AND** after the burst, the bubble SHALL shrink and trace a path toward the DNA Orb at the bottom
- **AND** the bubble SHALL be absorbed into the orb with a dissolve effect
- **AND** if comet trail is enabled by the current stage level, the bubble SHALL leave a colored trail along its path
- **AND** on absorption completion, the orb SHALL trigger a shockwave ring (if enabled by stage level)
- **AND** the orb's color SHALL incorporate the absorbed bubble's hue

#### Scenario: Color injection uses bubble's existing hue
- **WHEN** a bubble is absorbed into the orb
- **THEN** the orb SHALL absorb the same hue used to render that bubble's gradient
- **AND** 10-15 particles SHALL be replaced with the injected hue (with +/- 20 degree random variance)
- **AND** `swirlIntensity` SHALL spike to 1.0 for a transient visual burst
- **AND** the hue SHALL be appended to the color palette for use by orbital particles and light rays

#### Scenario: Orb visual evolution with stage-level escalation
- **WHEN** the user follows more artists
- **THEN** the orb's visual presentation SHALL be determined by a stage-parameter mapping keyed to the follow count
- **AND** the orb radius, orbital count, light ray count, breathing amplitude, and ground glow SHALL all be driven by the parameters for that stage
- **AND** each follow SHALL produce a visibly distinct escalation in effects

#### Scenario: First follow has maximum visual impact
- **WHEN** the user follows their first artist (followCount goes from 0 to 1)
- **THEN** the orb radius SHALL increase from 60 to 68
- **AND** the breathing pulse SHALL begin
- **AND** the visible particle count SHALL increase noticeably

#### Scenario: Effective swirl combines base and transient
- **WHEN** the orb animation loop runs
- **THEN** `baseIntensity` SHALL be computed as `1 - 1 / (1 + followCount * 0.5)` (diminishing returns curve)
- **AND** the particle speed multiplier SHALL be `1 + (baseIntensity + swirlIntensity) * 2`
- **AND** `swirlIntensity` SHALL decay over ~1000ms as before
- **AND** `baseIntensity` SHALL NOT decay within the same page session

### Requirement: Orb respects prefers-reduced-motion
The orb animation system SHALL respect the user's motion preferences.

#### Scenario: Reduced motion user follows an artist
- **WHEN** `prefers-reduced-motion: reduce` is active and a user follows an artist
- **THEN** `baseIntensity` SHALL still accumulate (color richness increases)
- **AND** the swirl speed multiplier SHALL remain at 1 (no acceleration)
- **AND** the `swirlIntensity` spike SHALL be suppressed

---

### Requirement: Combined spawn-and-absorb bubble action
The system SHALL expose a combined action that spawns a temporary bubble and immediately starts its absorption animation into the orb.

#### Scenario: Spawn-and-absorb creates and absorbs a bubble
- **WHEN** the spawn-and-absorb action is invoked for an artist at a given position
- **THEN** the canvas SHALL start the absorption animation from that position toward the orb center
- **AND** on completion, the canvas SHALL inject the artist's color into the orb
- **AND** the canvas SHALL **immediately** dispatch the `need-more-bubbles` custom event (not deferred until absorption completion)

### Requirement: Orb Activation Separates Gesture Celebration From Follow-Count State

The DNA orb's activation SHALL be gesture-driven: the orb SHALL enter Discovery dormant (its unobtrusive baseline) and SHALL advance its stage level and fire its celebration ONLY in response to a genuine follow gesture's bubble absorption completing on this screen. The orb's stage level SHALL be a function of the follow gestures completed during the current Discovery session — NOT of the user's total/historical follow count — so the orb never reads as "activated" before a genuine follow, regardless of how many artists the user already follows. Non-gesture follow-count changes (guest-follow hydration, guest→account migration, unfollow, optimistic-update rollback) SHALL NOT move the orb or fire the celebration. A stage-level update SHALL NOT reset in-flight transient effects.

The mapping from stage level to visual parameters is itself unchanged by this requirement; this requirement governs WHEN and HOW that mapping is applied and WHEN the celebration fires, not the mapping's values.

#### Scenario: Orb enters dormant regardless of total follow count

- **WHEN** the Discovery screen is entered
- **AND** the user already has N followed artists (e.g. restored/hydrated from a prior session before the canvas binds)
- **THEN** the orb SHALL render at its dormant baseline on first paint (the level-0 look: small radius, no orbitals, no light rays), NOT at the stage level for N
- **AND** no celebratory activation flash SHALL fire

#### Scenario: Non-gesture follow-count changes do not move the orb

- **WHEN** the follow count changes for a reason other than a follow gesture completing on this screen — for example guest-follow hydration, guest→account migration on sign-in, an unfollow, or an optimistic-update rollback
- **THEN** the orb SHALL NOT change its stage level
- **AND** no celebratory activation flash SHALL fire

#### Scenario: A genuine follow both advances the stage and celebrates

- **WHEN** a user follows an artist and the bubble absorption into the orb completes
- **THEN** the orb SHALL advance its stage level by one step (session-scoped) toward the new stage's targets
- **AND** the orb SHALL fire the celebratory activation together with the color injection, the shockwave (if enabled by the current stage level), and the landing tone on the same completion
- **AND** the follow-absorption completion SHALL be the only path that advances the stage or triggers the celebratory activation

#### Scenario: Unfollow does not move the orb or celebrate

- **WHEN** the follow count decreases because the user unfollows an artist
- **THEN** the orb SHALL NOT change its stage level
- **AND** no celebratory activation flash SHALL fire

#### Scenario: Stage transitions are eased and preserve transient effects

- **WHEN** a genuine follow advances the stage level
- **THEN** the orb's continuous visual quantities (e.g. radius, base intensity) SHALL transition smoothly toward the new stage's targets rather than snapping instantaneously
- **AND** in-flight transient effects such as particle trails SHALL NOT be reset by the stage-level change

#### Scenario: Zero follows this session is dormant with no spurious activation

- **WHEN** the user has not completed a follow on this screen this session
- **THEN** the orb SHALL present its unobtrusive baseline (the level-0 "small seed radius / unobtrusive" look), regardless of the user's total follow count
- **AND** no celebratory activation flash SHALL fire

### Requirement: Bubble Hue Injection into Orb Particles

When an artist bubble is absorbed into the DNA orb, the orb's particle system SHALL incorporate the bubble's hue, visually reflecting the followed artist's color identity.

#### Scenario: Follow triggers color injection

- **WHEN** an artist bubble completes its absorption animation into the orb center
- **THEN** the orb's particle system SHALL replace 5-8 existing particles with new particles at the absorbed bubble's hue
- **AND** the replacement SHALL keep the total particle count constant (no net growth)
- **AND** the new particles SHALL have randomized angle, radius, speed, size, and opacity within normal ranges

#### Scenario: Accumulated follows produce diverse orb colors

- **WHEN** a user has followed 3 artists with hues 142 (green), 287 (purple), and 35 (orange)
- **THEN** the orb SHALL contain particles in all three hue families mixed with the base hue range (220-280)
- **AND** the visual effect SHALL be a multi-colored particle swirl representing the user's "Music DNA"

#### Scenario: Hue comes from bubble's existing rendering color

- **WHEN** the absorption animation fires for a bubble
- **THEN** the hue applied to the orb's particle system SHALL be the same hue used to render that bubble on the canvas
- **AND** the system SHALL NOT re-compute the hue from the artist name

### Requirement: Swirl Animation on Follow

The orb SHALL play a swirl animation when a new artist color is injected, making the color mixing visually dynamic.

#### Scenario: Swirl triggers on color injection

- **WHEN** a new artist color is injected into the orb
- **THEN** the orb's particle rotation speed SHALL increase to 3x normal speed
- **AND** the speed boost SHALL decay smoothly back to 1x over approximately 1000ms
- **AND** the glow intensity SHALL temporarily increase by 0.4 (additive with pulse)

#### Scenario: Swirl during reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the color injection SHALL still occur (particles change hue)
- **BUT** the rotation speed boost SHALL be suppressed (remain at 1x)
- **AND** the glow intensity boost SHALL be suppressed

#### Scenario: Multiple rapid follows

- **WHEN** a user follows two artists in quick succession (within 1 second)
- **THEN** each follow SHALL inject its own color independently
- **AND** the swirl animations SHALL compound (speed boost restarts from 3x on each injection)
- **AND** the particle count SHALL remain constant

### Requirement: Stage-level escalation system
The system SHALL calculate visual effect parameters from the follow count using a stage-level model, where each follow advances the stage by one level. The calculation SHALL be implemented as a pure function, separate from rendering logic. Full visual intensity SHALL be reached at follow 5.

#### Scenario: Stage parameters at zero follows
- **WHEN** the follow count is 0
- **THEN** the stage parameters SHALL be: orb radius 60, orbital count 0, light ray count 0, ground glow intensity 0, shockwave effect off, comet trail effect off, nebula layer count 0, vortex trail length 0, beat tempo (BPM) 0, strobe effect off, orbital tail arc 0, and orbital size 2

#### Scenario: Stage parameters at one follow
- **WHEN** the follow count is 1
- **THEN** the stage parameters SHALL be: orb radius 72, breathing amplitude greater than 0, orbital count 2, particle visibility ratio greater than 0.3, ground glow intensity greater than 0, vortex trail length 2, and orbital size 4

#### Scenario: Stage parameters at two follows
- **WHEN** the follow count is 2
- **THEN** the stage parameters SHALL be: orbital count 5, light ray count 2, nebula layer count 1, beat tempo (BPM) greater than 0, and orbital tail arc greater than 0

#### Scenario: Stage parameters at three follows
- **WHEN** the follow count is 3
- **THEN** the stage parameters SHALL be: shockwave effect on, comet trail effect on, strobe effect on, vortex trail length 6, and light ray count 6

#### Scenario: Stage parameters at four follows
- **WHEN** the follow count is 4
- **THEN** the stage parameters SHALL be: nebula layer count 3, orbital tail arc 45, orbital size 8, and orbital count 11

#### Scenario: Stage parameters at five follows (full show)
- **WHEN** the follow count is 5
- **THEN** the stage parameters SHALL reach maximum intensity: light ray count 12 or more, orbital count 12, beat tempo (BPM) 2.0, light ray intensity 0.35 or more, and all effect features enabled

#### Scenario: Stage parameters at six or more follows
- **WHEN** the follow count is 6 or more
- **THEN** the stage parameters SHALL be the same maximum intensity values as follow 5 (all effects capped at full show level)

#### Scenario: Orb radius growth ceiling
- **WHEN** the follow count exceeds 20
- **THEN** the orb radius SHALL NOT exceed 120

#### Scenario: Stage params are deterministic
- **WHEN** the stage parameters are calculated multiple times with the same follow count
- **THEN** the result SHALL be identical each time (pure function, no side effects)

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
- **THEN** the renderer SHALL compute `beatPhase = Math.sin(time * beatBPM * 2 * Math.PI)` on each `update()`
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

### Requirement: Orb pulse on follow
The central Music DNA orb SHALL pulse each time an artist is followed, providing visual feedback that the selection was registered.

#### Scenario: Bubble tap triggers orb pulse
- **WHEN** a bubble is tapped and the follow operation succeeds
- **THEN** the orb SHALL respond to the updated follow count
- **AND** the orb SHALL play a pulse animation
- **AND** the orb's base glow intensity SHALL increase according to the easing curve
