## MODIFIED Requirements

### Requirement: Interactive Artist Discovery (Bubble Network UI)

The system SHALL provide an engaging, gamified interface for users to discover and follow artists using Last.fm API data. During onboarding, followed artists are stored locally (not via backend RPC). Additionally, the system SHALL trigger a background concert search for each followed artist to pre-populate concert data for the Dashboard.

#### Scenario: Guest user follows artist via bubble tap

- **WHEN** a guest user (in onboarding) taps an artist bubble
- **THEN** the system SHALL trigger the absorption animation
- **AND** the system SHALL store the artist in the `guest.follows` state slice via Store dispatch
- **AND** the system SHALL NOT call any backend RPC for the follow operation itself
- **AND** the system SHALL call `ConcertService/SearchNewConcerts` fire-and-forget in the background

#### Scenario: Discover to Dashboard transition

- **WHEN** a user is at Step `'discovery'`
- **AND** the user has followed >= 3 artists
- **AND** concert search results have been received for all followed artists (or timed out)
- **THEN** the system SHALL activate a coach mark spotlight on the Dashboard icon
- **AND** when the user taps the Dashboard icon, the system SHALL advance `onboardingStep` to `'dashboard'`
- **AND** the system SHALL navigate to `/dashboard`

#### Scenario: Pre-seeded follows on page reload

- **WHEN** the discovery page loads during onboarding
- **THEN** the system SHALL read pre-seeded follows from `store.getState().guest.follows`
- **AND** trigger concert searches for any artists not yet searched
