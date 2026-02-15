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
The system SHALL provide a gamified artist discovery interface using a "DNA Extraction" metaphor with an interactive orb (glass sphere) UI that collects user preferences.

#### Scenario: Initial bubble display with DNA Orb
- **WHEN** a user reaches the Artist Discovery step after authentication
- **THEN** the system SHALL display approximately 30 artist bubbles in the center area using physics-based animation
- **AND** the system SHALL display a "Music DNA Orb" (glass sphere UI) at the bottom of the screen
- **AND** the orb SHALL serve as a visual inventory for collected artists

---

### Requirement: Bubble Absorption Animation
The system SHALL provide satisfying visual feedback when users select artists by animating bubbles into the DNA Orb.

#### Scenario: Artist selection with absorption effect
- **WHEN** a user taps an artist bubble
- **THEN** the bubble SHALL shrink and trace a path toward the DNA Orb at the bottom
- **AND** the bubble SHALL be absorbed into the orb with a dissolve effect
- **AND** the orb's internal effects (swirling light, particles) SHALL intensify
- **AND** the orb's color SHALL become richer and brighter proportional to the number of followed artists

#### Scenario: Orb visual evolution
- **WHEN** the user follows more artists
- **THEN** the orb SHALL progressively fill with swirling particle effects
- **AND** the orb's glow intensity SHALL increase
- **AND** the color saturation SHALL deepen to reflect growing "Music DNA"

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
The system SHALL generate new artist recommendations dynamically using the backend ArtistService.ListSimilar RPC.

#### Scenario: Similar artist bubble spawning
- **WHEN** a user taps an artist bubble
- **THEN** the system SHALL call the backend `ArtistService.ListSimilar` RPC with the selected artist's ID
- **AND** new bubbles representing similar artists SHALL spawn from the original bubble's position
- **AND** the new bubbles SHALL appear with a "pop" emergence animation
- **AND** the new bubbles SHALL integrate into the physics-based layout

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
