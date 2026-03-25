## MODIFIED Requirements

### Requirement: Interactive Artist Discovery (Bubble Network UI)

The system SHALL provide an engaging, gamified interface for users to discover and follow artists using Last.fm API data. During onboarding, followed artists are stored locally (not via backend RPC). The system SHALL trigger a background concert search for each followed artist and track which artists have concerts. The Coach Mark SHALL appear when the progression condition is reached, remain visible for 2 seconds, then fade out. Navigation to the Dashboard is not triggered automatically — the user taps the Home nav tab at their own pace.

#### Scenario: Guest user follows artist via bubble tap

- **WHEN** a guest user (in onboarding) taps an artist bubble
- **THEN** the system SHALL trigger the absorption animation
- **AND** the system SHALL store the artist in `FollowServiceClient.followedArtists` (which delegates to `GuestService` for guest users)
- **AND** the system SHALL call `ConcertServiceClient.searchAndTrack(artistId)` to initiate background search and polling
- **AND** the system SHALL NOT call any backend RPC for the follow operation itself

#### Scenario: Guest follow default hype level

- **WHEN** a guest user (in onboarding) requests the list of followed artists via `listFollowed()`
- **THEN** the system SHALL return each followed artist with hype level `'watch'` (observation tier)

#### Scenario: Discover to Dashboard transition condition

- **WHEN** a user is at Step `'discovery'`
- **AND** either the user has followed 5 or more artists, OR `ConcertServiceClient.artistsWithConcertsCount` >= 3
- **THEN** the system SHALL activate a coach mark spotlight on the Dashboard icon for 2 seconds
- **AND** after 2 seconds the spotlight SHALL fade out automatically
- **AND** the user MAY tap the Dashboard icon at any time (including after the spotlight fades) to navigate to `/dashboard`
- **AND** when the user taps the Dashboard icon, the system SHALL advance `onboardingStep` to `'dashboard'`

#### Scenario: Coach Mark fades after 2 seconds

- **WHEN** the progression condition is first met
- **THEN** the system SHALL display the coach mark spotlight
- **AND** after 2000ms the system SHALL deactivate the spotlight
- **AND** the Dashboard nav icon SHALL remain tappable without the spotlight

#### Scenario: Coach Mark does not reappear

- **WHEN** the coach mark has already been shown for the current onboarding session
- **THEN** the system SHALL NOT display it again even if the user follows more artists

#### Scenario: Pre-seeded follows on page reload

- **WHEN** the discovery page loads during onboarding
- **THEN** the system SHALL hydrate follows from `GuestService.follows` into `FollowServiceClient`
- **AND** the system SHALL call `ConcertServiceClient.searchAndTrack()` for any artists not yet tracked

#### Scenario: Snack notification on concert found

- **WHEN** a followed artist's search completes with status `completed`
- **AND** `listConcerts(artistId)` returns at least one concert
- **THEN** the system SHALL display a snack notification indicating the artist has upcoming events

## MODIFIED Requirements

### Requirement: Step Sequence

The onboarding step sequence SHALL be LP → DISCOVERY → DASHBOARD → MY_ARTISTS → COMPLETED. The DETAIL step is removed.

#### Scenario: Step sequence excludes DETAIL

- **WHEN** `onboardingStep` is `'dashboard'`
- **AND** the DASHBOARD step completes (Celebration Overlay opens)
- **THEN** the system SHALL advance `onboardingStep` to `'my-artists'`
- **AND** the system SHALL NOT pass through any intermediate `'detail'` step

#### Scenario: Legacy localStorage value migration

- **WHEN** the system reads `liverty:onboardingStep` from localStorage
- **AND** the stored value is `'detail'`
- **THEN** the system SHALL treat it as `'dashboard'` for routing and step logic

## REMOVED Requirements

### Requirement: DETAIL onboarding step

**Reason**: The DETAIL step existed solely to spotlight the My Artists nav tab after a card tap. With card taps now correctly opening the Detail Sheet and guidance shifting to a pull model, this intermediate step is no longer needed. My Artists guidance is handled by PageHelp auto-open on first visit.

**Migration**: Remove `OnboardingStep.DETAIL` from the enum in `onboarding.ts`. Remove `'detail'` from `STEP_ROUTE_MAP`. Update all `isOnboardingStepDetail` checks. Add migration shim in `OnboardingStorage` to map stored `'detail'` → `'dashboard'`.
