## MODIFIED Requirements

### Requirement: Interactive Artist Discovery (Bubble Network UI)

The system SHALL provide an engaging, gamified interface for users to discover and follow artists using Last.fm API data. During onboarding, followed artists are stored locally (not via backend RPC). The system SHALL call `SearchNewConcerts` for each followed artist and track which artists have concerts. The Coach Mark SHALL appear as soon as the concert-with-artists target is reached.

#### Scenario: Guest user follows artist via bubble tap

- **WHEN** a guest user (in onboarding) taps an artist bubble
- **THEN** the system SHALL trigger the absorption animation
- **AND** the system SHALL store the artist in `FollowServiceClient.followedArtists` (which delegates to `GuestService` for guest users)
- **AND** the system SHALL call `searchNewConcerts(artistId)` and await the response (blocking until Gemini completes)
- **AND** if the response contains concerts, add the artist to `artistsWithConcerts`
- **AND** the system SHALL NOT call any backend RPC for the follow operation itself

#### Scenario: Guest follow default hype level

- **WHEN** a guest user (in onboarding) requests the list of followed artists via `listFollowed()`
- **THEN** the system SHALL return each followed artist with hype level `'watch'` (observation tier)

#### Scenario: Discover to Dashboard transition

- **WHEN** a user is at Step `'discovery'`
- **AND** `ConcertServiceClient.artistsWithConcertsCount` >= 3
- **THEN** the system SHALL activate a coach mark spotlight on the Dashboard icon
- **AND** when the user taps the Dashboard icon, the system SHALL advance `onboardingStep` to `'dashboard'`
- **AND** the system SHALL navigate to `/dashboard`

#### Scenario: Snack notification on concert found

- **WHEN** `searchNewConcerts(artistId)` returns a non-empty concerts list
- **THEN** the system SHALL display a snack notification indicating the artist has upcoming events

#### Scenario: Pre-seeded follows on page reload

- **WHEN** the discovery page loads during onboarding
- **THEN** the system SHALL hydrate follows from `GuestService.follows` into `FollowServiceClient`
- **AND** the system SHALL call `searchNewConcerts()` for each hydrated artist (concurrently)
- **AND** update `artistsWithConcerts` as each call completes

#### Scenario: Search failure does not block follow

- **WHEN** `searchNewConcerts(artistId)` fails or times out
- **THEN** the system SHALL log the error
- **AND** the follow operation itself SHALL remain successful
- **AND** the artist SHALL NOT be added to `artistsWithConcerts`
