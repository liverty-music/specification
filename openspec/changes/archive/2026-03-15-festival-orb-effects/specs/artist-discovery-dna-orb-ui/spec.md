# Artist Discovery DNA Orb UI — Delta

## MODIFIED Requirements

### Requirement: Bubble Absorption Animation
The system SHALL provide satisfying visual feedback when users select artists by animating bubbles into the DNA Orb, with accumulating visual intensity and comet trail effects.

#### Scenario: Artist selection with absorption effect
- **WHEN** a user taps an artist bubble
- **THEN** the bubble SHALL shrink and trace a path toward the DNA Orb at the bottom
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
- **THEN** the particle speed multiplier SHALL be `1 + (baseIntensity + swirlIntensity) * 2`
- **AND** `swirlIntensity` SHALL decay over ~1000ms as before
- **AND** `baseIntensity` SHALL NOT decay within the same page session

---

### Requirement: DNA Extraction UI Concept
The system SHALL provide a gamified artist discovery interface using a "DNA Extraction" metaphor with an interactive orb (glass sphere) UI that collects user preferences, with visual differentiation per artist and onboarding guidance.

#### Scenario: Initial bubble display with DNA Orb
- **WHEN** a user reaches the Artist Discovery step after authentication
- **THEN** the system SHALL display approximately 30 artist bubbles in the center area using physics-based animation
- **AND** the system SHALL display a "Music DNA Orb" (glass sphere UI) at the bottom of the screen
- **AND** the orb SHALL serve as a visual inventory for collected artists

#### Scenario: Per-artist bubble color differentiation
- **WHEN** artist bubbles are rendered
- **THEN** each bubble SHALL have a unique gradient color derived from the artist's name using a deterministic HSL-based algorithm
- **AND** the colors SHALL provide visual variety across the bubble field (not uniform purple)

#### Scenario: Onboarding guidance overlay
- **WHEN** the Artist Discovery screen is displayed for the first time during onboarding
- **THEN** the system SHALL display a popover guide explaining the interaction (per `onboarding-popover-guide` capability)
- **AND** the popover SHALL dismiss via light-dismiss or explicit close

#### Scenario: Background visual depth
- **WHEN** the Artist Discovery screen is displayed
- **THEN** the background SHALL include subtle visual elements (e.g., particle field, starfield, or animated gradient) to create depth
- **AND** these elements SHALL NOT compete with the foreground bubbles and orb for attention

## REMOVED Requirements

### Requirement: Orb label text
**Reason**: The "MUSIC DNA · N" label is removed to reduce visual clutter. The orb's growing size and escalating effects now communicate progress more effectively than a text label.
**Migration**: No migration needed. The orb-label DOM element and `.orb-label` CSS rules are deleted. The follow count is still available via the `followedCount` bindable for accessibility (screen reader status text).
