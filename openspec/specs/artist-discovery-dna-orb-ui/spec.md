# Artist Discovery DNA Orb UI

## Purpose

This capability defines the Artist Discovery UI for the Liverty Music MVP onboarding flow, featuring a gamified "DNA Extraction" metaphor. Users interact with physics-based artist bubbles that are absorbed into a visual "Music DNA Orb" inventory, creating an engaging way to collect music preferences and build personalized recommendations.

**Key Aspects:**
- Interactive canvas-based UI with physics-simulated artist bubbles
- DNA Orb visual metaphor that evolves as users follow artists
- Backend integration via ArtistService RPCs for artist data and recommendations
- Performance-optimized for 60fps on mobile devices

---

## Requirements

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

---

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

### Requirement: Orb respects prefers-reduced-motion
The orb animation system SHALL respect the user's motion preferences.

#### Scenario: Reduced motion user follows an artist
- **WHEN** `prefers-reduced-motion: reduce` is active and a user follows an artist
- **THEN** `baseIntensity` SHALL still accumulate (color richness increases)
- **AND** the swirl speed multiplier SHALL remain at 1 (no acceleration)
- **AND** the `swirlIntensity` spike SHALL be suppressed

---

### Requirement: Dynamic Toast Notifications for Live Events
The system SHALL provide instant feedback about available live events using dynamic toast notifications.

#### Scenario: Live event notification on artist follow
- **WHEN** a user taps an artist bubble
- **AND** the artist has upcoming live events in the database
- **THEN** the system SHALL display a dynamic toast notification from the top of the screen
- **AND** the toast SHALL show the message: "🎫 [Artist Name] has upcoming live events!"
- **AND** the toast SHALL remain visible for 2-3 seconds
- **AND** the toast SHALL fade out smoothly

#### Scenario: No notification for artists without events
- **WHEN** a user taps an artist bubble
- **AND** the artist has no upcoming live events in the database
- **THEN** the system SHALL NOT display a toast notification
- **AND** the bubble absorption animation SHALL proceed normally

---

### Requirement: Similar Artist Chain Reaction
The system SHALL generate new artist recommendations dynamically using the backend ArtistService.ListSimilar RPC with a limit parameter. The frontend SHALL call the Follow RPC when a user taps an artist bubble. The fetch SHALL NOT directly mutate the bubble pool — the caller SHALL manage eviction and insertion via `addToPool()`.

#### Scenario: Similar artist bubble spawning
- **WHEN** a user taps an artist bubble
- **THEN** the system SHALL call the backend `ArtistService.ListSimilar` RPC with the selected artist's ID and `limit=30`
- **AND** the system SHALL deduplicate the results (excluding seen and followed artists)
- **AND** the system SHALL add results to the pool via `addToPool()`, evicting oldest bubbles if the pool would exceed 50
- **AND** evicted bubbles SHALL be faded out before new bubbles spawn
- **AND** new bubbles representing similar artists SHALL spawn from the original bubble's position
- **AND** the new bubbles SHALL appear with a "pop" emergence animation
- **AND** the new bubbles SHALL integrate into the physics-based layout

#### Scenario: Follow RPC called on bubble tap
- **WHEN** a user taps an artist bubble
- **THEN** the frontend SHALL call `this.artistClient.follow({ artistId: new ArtistId({ value: artist.id }) })`
- **AND** the call SHALL be non-blocking (fire-and-forget with error logging)
- **AND** the local state SHALL update immediately without waiting for the RPC response

---

### Requirement: Completion Action via DNA Orb
The system SHALL use the DNA Orb as the primary navigation element to proceed to the dashboard.

#### Scenario: Dashboard navigation button
- **WHEN** the user has followed one or more artists
- **THEN** the system SHALL display a tappable button on or near the DNA Orb
- **AND** the button SHALL show the text: "[View Live Schedule (X artists)]" where X is the follow count
- **AND** when tapped, the system SHALL proceed to the Loading Sequence step

---

### Requirement: Physics-Based Bubble Animation
The system SHALL implement smooth, natural bubble movement using physics simulation.

#### Scenario: Realistic bubble physics
- **WHEN** artist bubbles are displayed
- **THEN** the system SHALL use a physics engine (e.g., Matter.js, D3.js force simulation)
- **AND** bubbles SHALL float, bounce, and interact naturally
- **AND** performance SHALL be optimized for mobile devices using component optimization or Canvas/WebGL rendering

---

### Requirement: List followed artists from backend
The `ArtistDiscoveryService.listFollowedFromBackend` method SHALL use the instance's `artistClient` to fetch followed artists from the backend.

#### Scenario: Fetching followed artists
- **WHEN** `listFollowedFromBackend` is called
- **THEN** it SHALL call `this.artistClient.listFollowed()` (not the unscoped `artistClient` variable)

#### Scenario: Bug fix verification
- **WHEN** a test calls `listFollowedFromBackend`
- **THEN** it SHALL NOT throw a `ReferenceError` for undefined `artistClient`

---

## Technical Context

This specification defines the Artist Discovery UI for Liverty Music MVP, featuring:
- **UI Metaphor**: "DNA Extraction" - collecting user music preferences as genetic material
- **Core Component**: Music DNA Orb (glass sphere) that visually accumulates user taste
- **Data Source**: Backend `ArtistService` RPCs (`ListTop`, `ListSimilar`) via Connect-RPC
- **Animation Requirements**: Physics-based bubbles, absorption effects, particle systems
- **Performance Target**: Smooth 60fps on mobile devices

## Reference Documentation

For detailed visual design, animation specs, and UI behavior, see:
- `../../changes/archive/2026-02-15-frontend-artist-discovery-ui/docs/onboarding-ux.md` (Japanese detailed specification - Step 2)
