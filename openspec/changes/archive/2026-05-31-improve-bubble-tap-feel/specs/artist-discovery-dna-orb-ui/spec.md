## MODIFIED Requirements

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
- **THEN** `OrbRenderer.injectColor` SHALL be called with the same hue used to render that bubble's gradient
- **AND** 10-15 particles SHALL be replaced with the injected hue (with +/- 20 degree random variance)
- **AND** `swirlIntensity` SHALL spike to 1.0 for a transient visual burst
- **AND** the hue SHALL be appended to the color palette for use by orbital particles and light rays

#### Scenario: Orb visual evolution with stage-level escalation
- **WHEN** the user follows more artists
- **THEN** the orb's visual presentation SHALL be determined by `getStageParams(followCount)` from `stage-effects.ts`
- **AND** the orb radius, orbital count, light ray count, breathing amplitude, and ground glow SHALL all be driven by the returned `StageParams`
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

## ADDED Requirements

### Requirement: Bubble Burst On Tap

When a user taps an artist bubble, the system SHALL play a burst effect that makes the bubble visibly pop in place before the absorption-into-orb animation continues, providing tactile "pop" feedback while preserving the orb color-injection metaphor.

#### Scenario: Bubble over-inflates then ruptures

- **WHEN** a user taps an artist bubble
- **THEN** the bubble SHALL briefly over-inflate (scale up beyond its rest size) as a short anticipation before rupturing
- **AND** a bright rupture ring plus an additive light bloom SHALL flash open at the burst point so the burst reads as a pop of light
- **AND** the over-inflation SHALL replace the previous horizontal squash anticipation

#### Scenario: Burst sprays luminous droplets in the bubble's hue

- **WHEN** the bubble ruptures
- **THEN** a spray of droplet particles (on the order of 15–20) SHALL be emitted immediately at the tap point
- **AND** the droplets SHALL be tinted with the tapped bubble's own hue but rendered luminously (additive glow with a white-hot core) so they read as sparks of light rather than flat same-color dots
- **AND** the droplets SHALL travel outward with a slight downward gravity so they arc like flung liquid, then fade out

#### Scenario: Burst hands off to absorption

- **WHEN** the burst anticipation reaches its peak
- **THEN** the existing absorption animation SHALL start (shrink, comet trail, color injection, shockwave) so the artist's color still flies into the orb

#### Scenario: Reduced motion suppresses the burst

- **WHEN** the user has `prefers-reduced-motion` enabled and taps a bubble
- **THEN** the over-inflation, rupture ring, and droplet spray SHALL be suppressed
- **AND** the interaction SHALL proceed directly to absorption, consistent with the existing reduced-motion handling
