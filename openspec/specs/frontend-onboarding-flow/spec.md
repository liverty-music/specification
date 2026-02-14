## Purpose

This capability defines the complete user onboarding experience for Liverty Music MVP, guiding new users from landing page through authentication, artist discovery, and personalized dashboard setup with a focus on eliminating FOMO for live music events.

## Requirements

### Requirement: Landing Page with Authentication
The system SHALL provide a landing page that communicates the service value proposition and enables user authentication via Zitadel (Google OAuth provider).

#### Scenario: First-time user visits landing page
- **WHEN** a user accesses the application for the first time
- **THEN** the system SHALL display a hero message communicating the core value ("Never miss your favorite artist's live show again")
- **AND** the system SHALL provide a single "Continue with Google" authentication button
- **AND** the system SHALL NOT require Spotify, Apple Music, or YouTube OAuth (out of MVP scope)

#### Scenario: User initiates Google authentication via Zitadel
- **WHEN** a user clicks the "Continue with Google" button
- **THEN** the system SHALL redirect the user to Zitadel OAuth flow with Google as the identity provider
- **AND** upon successful authentication, Zitadel SHALL create or retrieve the user account
- **AND** the system SHALL proceed to the Artist Discovery step

---

### Requirement: Just-in-Time Region Configuration
The system SHALL collect the user's primary residential area using a Just-in-Time approach, presenting the region selector as an overlay on the dashboard to minimize setup friction.

#### Scenario: Region setup overlay on first dashboard access
- **WHEN** the user completes the Loading Sequence and accesses the Dashboard for the first time
- **AND** the user has not yet configured their region
- **THEN** the system SHALL display the Dashboard with a blurred background
- **AND** the system SHALL present a bottom sheet overlay with the message "To find live events near you, tell us your main area"
- **AND** the system SHALL provide a prefecture dropdown selector or quick-select buttons for major cities

#### Scenario: Magic moment after region selection
- **WHEN** the user selects their region in the bottom sheet
- **THEN** the system SHALL immediately close the bottom sheet
- **AND** the system SHALL unblur the Dashboard background
- **AND** the system SHALL dynamically populate the Live Highway UI with region-relevant events
- **AND** this SHALL create a "magic moment" where personalized content appears instantly

---

### Requirement: Interactive Artist Discovery (Bubble Network UI)
The system SHALL provide an engaging, gamified interface for users to discover and follow artists using Last.fm API data.

#### Scenario: Initial artist bubble display
- **WHEN** a user reaches the Artist Discovery step
- **THEN** the system SHALL call Last.fm's `geo.getTopArtists` API with `country=japan`
- **AND** the system SHALL display approximately 30 top artists as floating circular bubbles with physics-based animation
- **AND** each bubble SHALL contain the artist's image and name

#### Scenario: User selects an artist (Follow action)
- **WHEN** a user taps an artist bubble
- **THEN** the system SHALL highlight the bubble to indicate selection
- **AND** the system SHALL query the internal database for upcoming live events for that artist
- **AND** if upcoming events exist, the system SHALL display a small "[📅 Live Available]" badge on the bubble with animation

#### Scenario: Similar artist chain reaction
- **WHEN** a user selects an artist bubble
- **THEN** the system SHALL call Last.fm's `artist.getSimilar` API using the selected artist as the seed
- **AND** the system SHALL spawn smaller bubbles representing similar artists, visually appearing to "split" from the parent bubble
- **AND** the new bubbles SHALL integrate into the physics-based layout

#### Scenario: Completing artist selection
- **WHEN** a user has selected one or more artists
- **THEN** the system SHALL display a persistent floating button at the bottom of the screen showing "[Create Dashboard (X artists following)]"
- **AND** when the user taps this button, the system SHALL proceed to the Loading Sequence step

---

### Requirement: Loading Sequence with Benevolent Deception
The system SHALL provide an engaging loading experience during data aggregation to maintain user engagement during processing time (3-10 seconds).

#### Scenario: Data loading with progressive messaging
- **WHEN** the system begins aggregating live event data for followed artists
- **THEN** the system SHALL display a multi-step animated loading sequence (NOT a simple spinner)
- **AND** Step 1 (0-2s) SHALL display: "Building your Music DNA..."
- **AND** Step 2 (2-5s) SHALL display: "Cross-referencing national live schedules..."
- **AND** Step 3 (5s+) SHALL display: "AI searching for latest tour info... 🤖"
- **AND** the system SHALL enforce a minimum 3-second display duration even if data loading completes earlier
- **AND** the system SHALL query the internal database and invoke Gemini API (with Grounding) for artists without existing event data

#### Scenario: Loading timeout handling
- **WHEN** data loading exceeds 10 seconds
- **THEN** the system SHALL terminate the loading process
- **AND** the system SHALL proceed to the Dashboard with only the successfully retrieved artist data
- **AND** the system SHALL NOT display an infinite loading state

---

### Requirement: Live Dashboard (Live Highway UI)
The system SHALL provide an intuitive, vertically-scrollable dashboard displaying live events organized by date and geographical proximity.

#### Scenario: Dashboard layout structure
- **WHEN** a user reaches the dashboard
- **THEN** the system SHALL display a 3-column timeline layout with vertical (date) axis
- **AND** Lane 1 "My City" (45-50% width) SHALL display events in the user's registered prefecture with large cards (artist image, date, venue)
- **AND** Lane 2 "My Region" (30% width) SHALL display events in the same geographical region (e.g., Kanto, Kansai) with medium cards (date, venue, artist name)
- **AND** Lane 3 "Others" (20% width) SHALL display all other nationwide events with small text labels (city name only)
- **AND** the layout SHALL be optimized for mobile portrait orientation with one-handed scrolling
- **AND** the system SHALL NOT allow horizontal scrolling

#### Scenario: Event card action buttons (MVP constraints)
- **WHEN** a user views an event card
- **THEN** the card SHALL NOT include ticket purchase buttons or links (data not available in MVP)
- **AND** the card SHALL provide a "[🔗 View Official Info]" button linking to the source website or social media
- **AND** the card SHALL provide a "[📅 Add to Calendar]" button to export the event to the device's native calendar (Google/iOS)

#### Scenario: Other lane event details
- **WHEN** a user taps a small event label in Lane 3 "Others"
- **THEN** the system SHALL display a modal with full event details

---

### Requirement: Contextual Engagement Prompts
The system SHALL request system permissions at contextually appropriate moments to avoid permission fatigue during initial onboarding.

#### Scenario: Push notification permission request
- **WHEN** a user taps a "[🔗 View Official Info]" button on any live event card for the first time
- **THEN** upon returning to the app, the system SHALL display a custom modal with context: "Get notified when this artist announces their next tour?"
- **AND** after the user interacts with the custom modal, the system SHALL trigger the browser's native push notification permission dialog

#### Scenario: PWA installation prompt
- **WHEN** a user visits the application for the second time (second session)
- **THEN** the system SHALL display a subtle toast notification at the bottom of the screen suggesting: "Add to home screen for easier access"
- **AND** the prompt SHALL be non-intrusive and dismissible

---

### Requirement: Performance and Mobile Optimization
The system SHALL ensure optimal performance and mobile-first design across all onboarding steps.

#### Scenario: Bubble UI performance optimization
- **WHEN** rendering the Artist Discovery Bubble UI with numerous DOM elements
- **THEN** the system SHALL implement render optimization techniques (e.g., React.memo, appropriate state management, or Canvas API)
- **AND** the system SHALL maintain smooth animation performance on mobile devices

#### Scenario: Mobile-first responsive design
- **WHEN** the application is accessed on a smartphone
- **THEN** the system SHALL render all UI components optimized for portrait orientation
- **AND** the system SHALL use CSS Grid/Flexbox for layout without triggering horizontal scrolling
- **AND** the Live Dashboard SHALL be designed for one-handed vertical scrolling

---

## Technical Context

This specification defines the frontend user onboarding experience for Liverty Music MVP, focusing on:
- **Pain Killer Product Goal**: Eliminate FOMO (Fear of Missing Out) for music fans regarding live events
- **MVP Scope**: Event discovery and referral to official sites (NO ticket sales)
- **Target Platform**: Progressive Web App (PWA) optimized for mobile devices
- **Data Sources**: Last.fm API (unauthenticated), internal database, Gemini API (fallback)
- **Authentication**: Zitadel with Google OAuth provider (Spotify/Apple Music/YouTube out of scope)

## Reference Documentation

For detailed UI/UX wireframes, copy text, and visual design specifications, see:
- `docs/onboarding-ux.md` (Japanese language detailed specification)
