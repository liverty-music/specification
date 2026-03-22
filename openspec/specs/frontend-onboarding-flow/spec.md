## MODIFIED Requirements

### Requirement: Interactive Artist Discovery (Bubble Network UI)

The system SHALL provide an engaging, gamified interface for users to discover and follow artists using Last.fm API data. During onboarding, followed artists are stored locally (not via backend RPC). The system SHALL trigger a background concert search for each followed artist and track which artists have concerts. The Coach Mark SHALL appear as soon as the concert-with-artists target is reached, independent of how many artists the user has followed or how many searches are still pending.

#### Scenario: Guest user follows artist via bubble tap

- **WHEN** a guest user (in onboarding) taps an artist bubble
- **THEN** the system SHALL trigger the absorption animation
- **AND** the system SHALL store the artist in `FollowServiceClient.followedArtists` (which delegates to `GuestService` for guest users)
- **AND** the system SHALL call `ConcertServiceClient.searchAndTrack(artistId)` to initiate background search and polling
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

#### Scenario: Coach Mark appears immediately at target

- **WHEN** a user has followed 5 artists
- **AND** 3 artists' searches have completed with concerts found
- **AND** 2 artists' searches are still pending
- **THEN** the system SHALL display the Coach Mark immediately
- **AND** the system SHALL NOT wait for the remaining 2 searches to complete

#### Scenario: Coach Mark does not appear without enough concerts

- **WHEN** a user has followed >= 3 artists
- **AND** fewer than 3 artists have concerts found (regardless of search completion status)
- **THEN** the system SHALL NOT display the Coach Mark

#### Scenario: Pre-seeded follows on page reload

- **WHEN** the discovery page loads during onboarding
- **THEN** the system SHALL hydrate follows from `GuestService.follows` into `FollowServiceClient`
- **AND** the system SHALL call `ConcertServiceClient.searchAndTrack()` for any artists not yet tracked

#### Scenario: Snack notification on concert found

- **WHEN** a followed artist's search completes with status `completed`
- **AND** `listConcerts(artistId)` returns at least one concert
- **THEN** the system SHALL display a snack notification indicating the artist has upcoming events
