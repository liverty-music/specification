## MODIFIED Requirements

### Requirement: Interactive Artist Discovery (Bubble Network UI)

The system SHALL provide an engaging, gamified interface for users to discover and follow artists using Last.fm API data. During the tutorial, followed artists are stored locally (not via backend RPC). Additionally, the system SHALL trigger a background concert search for each followed artist to pre-populate concert data for the Dashboard.

#### Scenario: Initial artist bubble display

- **WHEN** a user reaches the Artist Discovery step (Step 1)
- **THEN** the system SHALL call Last.fm's `geo.getTopArtists` API with `country=japan`
- **AND** the system SHALL display approximately 30 top artists as floating circular bubbles with physics-based animation

#### Scenario: Guest user follows artist via bubble tap

- **WHEN** a guest user (in tutorial) taps an artist bubble
- **THEN** the system SHALL trigger the absorption animation
- **AND** the system SHALL store the artist in `liverty:guest:followedArtists` in LocalStorage
- **AND** the system SHALL NOT call any backend RPC for the follow operation itself
- **AND** the system SHALL call `ConcertService/SearchNewConcerts` fire-and-forget in the background
- **AND** errors from `SearchNewConcerts` SHALL be logged to console and NOT affect the follow operation or UI

#### Scenario: Progress bar reaches target

- **WHEN** the user has followed 3 or more artists
- **THEN** the system SHALL display the progress bar at 100%
- **AND** the system SHALL activate and highlight the [Generate Dashboard] CTA button

#### Scenario: Discover to Dashboard transition

- **WHEN** a user is at Step 1 (Artist Discovery)
- **AND** the user has followed >= 3 artists
- **AND** the user taps the [Generate Dashboard] CTA
- **THEN** the system SHALL set `onboardingStep` to 3 (DASHBOARD)
- **AND** the system SHALL navigate to `/dashboard`

#### Scenario: Concert data availability at Dashboard

- **WHEN** the user arrives at the Dashboard after completing Artist Discovery
- **THEN** concert data MAY already be available from the fire-and-forget `SearchNewConcerts` calls triggered during artist follows in Discovery
- **AND** the Dashboard SHALL display its own loading skeleton / promise states for any data still pending
