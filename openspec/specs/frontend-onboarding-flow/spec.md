## Purpose

This capability defines the complete user onboarding experience for Liverty Music MVP, guiding new users from landing page through authentication, artist discovery, and personalized dashboard setup with a focus on eliminating FOMO for live music events.

## Requirements

### Requirement: Landing Page with Authentication
The system SHALL provide a landing page that communicates the service value proposition and enables user authentication via Zitadel (Passkey authentication), with post-authentication routing based on onboarding completion status.

#### Scenario: First-time user visits landing page
- **WHEN** a user accesses the application for the first time
- **THEN** the system SHALL display a hero message communicating the core value ("大好きなあのバンドのライブ、もう二度と見逃さない。")
- **AND** the system SHALL display a sub-message ("あなたの推しアーティストを登録するだけで、全国のライブ日程を自動収集。")
- **AND** the system SHALL provide "Sign Up" and "Sign In" buttons for Passkey authentication
- **AND** the system SHALL NOT provide Google, Spotify, Apple Music, or YouTube OAuth (out of MVP scope)

#### Scenario: User initiates Passkey authentication via Zitadel
- **WHEN** a user clicks the "Sign Up" or "Sign In" button
- **THEN** the system SHALL redirect the user to Zitadel OIDC flow for Passkey authentication
- **AND** upon successful authentication, Zitadel SHALL create or retrieve the user account
- **AND** the system SHALL check onboarding completion status
- **AND** if incomplete, the system SHALL redirect to the Artist Discovery step
- **AND** if complete, the system SHALL redirect to the Dashboard

---

### Requirement: Just-in-Time Region Configuration
The system SHALL collect the user's primary residential area using a Just-in-Time approach, presenting the region selector as an overlay on the dashboard to minimize setup friction.

#### Scenario: Region setup overlay on first dashboard access
- **WHEN** the user completes the Loading Sequence and accesses the Dashboard for the first time
- **AND** the user has not yet configured their region
- **THEN** the system SHALL display the Dashboard with a blurred background
- **AND** the system SHALL present a bottom sheet overlay with the message "To find live events near you, tell us your main area"
- **AND** the system SHALL provide a prefecture dropdown selector or quick-select buttons for major cities
- **AND** the bottom sheet SHALL use the design system's dark surface palette and sheet radius token

#### Scenario: Magic moment after region selection
- **WHEN** the user selects their region in the bottom sheet
- **THEN** the system SHALL immediately close the bottom sheet
- **AND** the system SHALL unblur the Dashboard background with a smooth transition animation
- **AND** the system SHALL dynamically populate the Live Highway UI with region-relevant events
- **AND** this SHALL create a "magic moment" where personalized content appears instantly

---

### Requirement: Interactive Artist Discovery (Bubble Network UI)
The system SHALL provide an engaging, gamified interface for users to discover and follow artists using Last.fm API data. The `loading()` lifecycle hook SHALL handle errors gracefully instead of crashing to a white screen.

#### Scenario: Initial artist bubble display
- **WHEN** a user reaches the Artist Discovery step
- **THEN** the system SHALL call Last.fm's `geo.getTopArtists` API with `country=japan`
- **AND** the system SHALL display approximately 30 top artists as floating circular bubbles with physics-based animation
- **AND** each bubble SHALL contain the artist's image and name

#### Scenario: Artist loading fails with error recovery
- **WHEN** the initial artist loading fails due to a network or API error
- **THEN** the system SHALL display an error state with the message and a "Retry" button
- **AND** the system SHALL NOT show a white screen
- **AND** the template SHALL use `promise.bind` to declaratively handle pending, success, and error states

#### Scenario: User selects an artist (Follow action)
- **WHEN** a user taps an artist bubble
- **THEN** the system SHALL highlight the bubble to indicate selection
- **AND** the system SHALL query the internal database for upcoming live events for that artist
- **AND** if upcoming events exist, the system SHALL display a small "[Live Available]" badge on the bubble with animation

#### Scenario: Similar artist chain reaction
- **WHEN** a user selects an artist bubble
- **THEN** the system SHALL call Last.fm's `artist.getSimilar` API using the selected artist as the seed
- **AND** the system SHALL spawn smaller bubbles representing similar artists, visually appearing to "split" from the parent bubble
- **AND** the new bubbles SHALL integrate into the physics-based layout

#### Scenario: Similar artist loading fails gracefully
- **WHEN** the similar artist API call fails
- **THEN** the system SHALL display a toast notification indicating the failure
- **AND** the system SHALL NOT crash or remove already-displayed bubbles
- **AND** the user SHALL be able to continue selecting other artists

#### Scenario: Artist follow RPC fails with rollback
- **WHEN** the fire-and-forget artist follow RPC call fails
- **THEN** the system SHALL display a toast notification "Failed to follow artist. Please try again."
- **AND** the system SHALL revert the local follow state (un-highlight the bubble)

#### Scenario: Completing artist selection
- **WHEN** a user has selected one or more artists
- **THEN** the system SHALL display a persistent floating button at the bottom of the screen showing "[Create Dashboard (X artists following)]"
- **AND** when the user taps this button, the system SHALL proceed to the Loading Sequence step

---

### Requirement: Loading Sequence with Benevolent Deception
The system SHALL provide an engaging loading experience during data aggregation to maintain user engagement during processing time (3-10 seconds). Data aggregation failures SHALL be communicated to the user instead of silently swallowed.

#### Scenario: Data loading with progressive messaging
- **WHEN** the system begins aggregating live event data for followed artists
- **THEN** the system SHALL display a multi-step animated loading sequence (NOT a simple spinner)
- **AND** Phase 1 (0-2s) SHALL display: "あなたのMusic DNAを構築中..."
- **AND** Phase 2 (2-5s) SHALL display: "全国のライブスケジュールと照合中..."
- **AND** Phase 3 (5s+) SHALL display: "AIが最新のツアー情報を検索中..."
- **AND** the system SHALL enforce a minimum 3-second display duration even if data loading completes earlier
- **AND** the system SHALL call `SearchNewConcerts` for each followed artist in parallel
- **AND** the system SHALL use a 10-second global timeout via `AbortController`
- **AND** the system SHALL display a visual progress indicator advancing through the phases

#### Scenario: Loading timeout handling
- **WHEN** data loading exceeds 10 seconds
- **THEN** the system SHALL terminate all remaining search requests
- **AND** the system SHALL proceed to the Dashboard with only the successfully retrieved artist data
- **AND** the system SHALL NOT display an infinite loading state

#### Scenario: Data aggregation partial failure
- **WHEN** some but not all `SearchNewConcerts` calls fail during loading
- **THEN** the system SHALL proceed to the Dashboard with successfully retrieved data
- **AND** the system SHALL display a toast notification on the Dashboard indicating partial data: "Some concert data could not be loaded"

#### Scenario: Data aggregation complete failure
- **WHEN** all `SearchNewConcerts` calls fail during loading
- **THEN** the system SHALL still navigate to the Dashboard
- **AND** the system SHALL display an error banner on the Dashboard indicating the failure with a "Retry" action

#### Scenario: Transition from Artist Discovery
- **WHEN** the user completes the Artist Discovery step
- **THEN** the system SHALL navigate to `/onboarding/loading`
- **AND** the loading sequence SHALL automatically begin data aggregation
- **AND** upon completion, the system SHALL navigate to the Dashboard

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
