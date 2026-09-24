<!-- spec: artist-discovery-dna-orb-ui | target: components/infrastructure/fan/web/global/dna-orb | flags: CLASSNAME | new_name: Bubble Absorption Animation -->

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
