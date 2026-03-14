## MODIFIED Requirements

### Requirement: Bubble Absorption Animation
The system SHALL provide satisfying visual feedback when users select artists by animating bubbles into the DNA Orb, with accumulating visual intensity.

#### Scenario: Artist selection with absorption effect
- **WHEN** a user taps an artist bubble
- **THEN** the bubble SHALL shrink and trace a path toward the DNA Orb at the bottom
- **AND** the bubble SHALL be absorbed into the orb with a dissolve effect
- **AND** the orb's internal effects (swirling light, particles) SHALL intensify
- **AND** the orb's color SHALL incorporate the absorbed bubble's hue (from the existing `artistHue` computation)

#### Scenario: Color injection uses bubble's existing hue
- **WHEN** a bubble is absorbed into the orb
- **THEN** `OrbRenderer.injectColor` SHALL be called with the same hue used to render that bubble's gradient
- **AND** 10-15 particles (previously 5-8) SHALL be replaced with the injected hue (with +/- 20 degree random variance)
- **AND** `swirlIntensity` SHALL spike to 1.0 for a transient visual burst

#### Scenario: Orb visual evolution with accumulating baseIntensity
- **WHEN** the user follows more artists
- **THEN** `OrbRenderer.baseIntensity` SHALL increase per follow using the formula: `baseIntensity = 1 - 1 / (1 + followCount * 0.5)`
- **AND** the effective intensity for glow, particle count, and swirl speed SHALL be computed as `intensity + baseIntensity`
- **AND** `swirlIntensity` spike decay SHALL apply on top of the elevated base, making each successive follow's swirl more dramatic

#### Scenario: First follow has maximum visual impact
- **WHEN** the user follows their first artist (followCount goes from 0 to 1)
- **THEN** `baseIntensity` SHALL jump from 0.00 to 0.33 (the largest single-follow delta)
- **AND** the visible particle count SHALL increase noticeably (from ~10% to ~40% of max)
- **AND** the orb glow radius SHALL expand visibly

#### Scenario: Diminishing returns on later follows
- **WHEN** the user follows their 5th artist
- **THEN** `baseIntensity` SHALL be approximately 0.71
- **AND** the delta from the 4th follow SHALL be approximately +0.05
- **AND** the orb SHALL still show a transient `swirlIntensity` spike and color injection, even though the base level change is small

#### Scenario: baseIntensity resets on page navigation
- **WHEN** the user navigates away from the discover page and returns
- **THEN** `baseIntensity` SHALL reset to 0
- **AND** `followCount` for intensity purposes SHALL reset to 0
- **AND** the orb SHALL start from its default visual state

#### Scenario: Effective swirl combines base and transient
- **WHEN** the orb animation loop runs
- **THEN** the particle speed multiplier SHALL be `1 + (baseIntensity + swirlIntensity) * 2`
- **AND** `swirlIntensity` SHALL decay over ~1000ms as before
- **AND** `baseIntensity` SHALL NOT decay within the same page session

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

#### Scenario: Orb label text
- **WHEN** the DNA Orb is displayed
- **THEN** the system SHALL display a label near the orb indicating its purpose (e.g., "Music DNA" or the current follow count)
- **AND** the label SHALL update dynamically as artists are followed

#### Scenario: Background visual depth
- **WHEN** the Artist Discovery screen is displayed
- **THEN** the background SHALL include subtle visual elements (e.g., particle field, starfield, or animated gradient) to create depth
- **AND** these elements SHALL NOT compete with the foreground bubbles and orb for attention

### Requirement: Orb respects prefers-reduced-motion
The orb animation system SHALL respect the user's motion preferences.

#### Scenario: Reduced motion user follows an artist
- **WHEN** `prefers-reduced-motion: reduce` is active and a user follows an artist
- **THEN** `baseIntensity` SHALL still accumulate (color richness increases)
- **AND** the swirl speed multiplier SHALL remain at 1 (no acceleration)
- **AND** the `swirlIntensity` spike SHALL be suppressed
