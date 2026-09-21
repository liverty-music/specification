<!-- spec: frontend-onboarding-flow | target: components/infrastructure/fan/web/route/discovery | flags: CLASSNAME | new_name: Interactive Artist Discovery (Bubble Network UI) -->

### Requirement: Interactive Artist Discovery (Bubble Network UI)

The system SHALL provide an engaging, gamified interface for users to discover and follow artists using Last.fm API data. During onboarding, followed artists are stored locally (not via backend RPC). The system SHALL trigger a background concert search for each followed artist and track which artists have concerts. The Coach Mark SHALL appear when the progression condition is reached and SHALL hint that the personal timetable is ready; it is owned by `CoachMarkService` (see `onboarding-spotlight`). Navigation to the Dashboard is never forced — the dashboard is always reachable and the user taps the Home nav tab at their own pace. Tapping the coach mark target SHALL navigate only; it SHALL NOT advance any onboarding step (there is no step machine).

#### Scenario: Guest user follows artist via bubble tap

- **WHEN** a guest user (in onboarding) taps an artist bubble
- **THEN** the system SHALL trigger the absorption animation
- **AND** the system SHALL store the artist locally (routed to the guest follow queue for unauthenticated users)
- **AND** the system SHALL initiate a background concert search/track for the artist via `ConcertService`
- **AND** the system SHALL NOT call any backend RPC for the follow operation itself

#### Scenario: Guest follow default hype level

- **WHEN** a guest user (in onboarding) requests the list of followed artists
- **THEN** the system SHALL return each followed artist with hype level `'watch'` (observation tier)

#### Scenario: Discover to Dashboard coach-mark trigger

- **WHEN** a user is in onboarding (`isOnboarding === true`)
- **AND** either the user has followed 5 or more artists, OR the live `artistsWithConcertsCount` >= 3
- **AND** the coach mark has not yet been shown this session
- **THEN** the system SHALL activate a coach mark spotlight on the Dashboard nav icon via `CoachMarkService`
- **AND** the trigger SHALL be evaluated from live follow/concert counts on the Discovery screen, not from a mirrored count cache
- **AND** the user MAY tap the Dashboard icon at any time (with or without the spotlight) to navigate to `/dashboard`
- **AND** tapping the Dashboard icon SHALL navigate only and SHALL NOT advance any onboarding step

#### Scenario: Coach Mark does not reappear

- **WHEN** the coach mark has already been shown for the current onboarding session
- **THEN** the system SHALL NOT display it again even if the user follows more artists

#### Scenario: Pre-seeded follows on page reload

- **WHEN** the discovery page loads during onboarding
- **THEN** the system SHALL hydrate follows from the locally stored guest follows into the active follow list
- **AND** the system SHALL initiate a concert search via `ConcertService` for any artists not yet tracked

#### Scenario: Snack notification on concert found

- **WHEN** a followed artist's search completes with status `completed`
- **AND** `listConcerts(artistId)` returns at least one concert
- **THEN** the system SHALL display a snack notification indicating the artist has upcoming events
