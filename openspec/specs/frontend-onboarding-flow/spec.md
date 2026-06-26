# Frontend Onboarding Flow

## Purpose

Defines the guest onboarding flow: interactive artist discovery, the linear onboarding step sequence (LP → DISCOVERY → DASHBOARD → MY_ARTISTS → … → COMPLETED), and the local-storage-backed progression that precedes account creation.
## Requirements
### Requirement: Interactive Artist Discovery (Bubble Network UI)

The system SHALL provide an engaging, gamified interface for users to discover and follow artists using Last.fm API data. During onboarding, followed artists are stored locally (not via backend RPC). The system SHALL trigger a background concert search for each followed artist and track which artists have concerts. The Coach Mark SHALL appear when the progression condition is reached and SHALL hint that the personal timetable is ready; it is owned by `CoachMarkService` (see `onboarding-spotlight`). Navigation to the Dashboard is never forced — the dashboard is always reachable and the user taps the Home nav tab at their own pace. Tapping the coach mark target SHALL navigate only; it SHALL NOT advance any onboarding step (there is no step machine).

#### Scenario: Guest user follows artist via bubble tap

- **WHEN** a guest user (in onboarding) taps an artist bubble
- **THEN** the system SHALL trigger the absorption animation
- **AND** the system SHALL store the artist via `FollowStore` (which routes to the guest queue for unauthenticated users)
- **AND** the system SHALL initiate a background concert search/track for the artist via `ConcertService`
- **AND** the system SHALL NOT call any backend RPC for the follow operation itself

#### Scenario: Guest follow default hype level

- **WHEN** a guest user (in onboarding) requests the list of followed artists via `FollowStore.listFollowed()`
- **THEN** the system SHALL return each followed artist with hype level `'watch'` (observation tier)

#### Scenario: Discover to Dashboard coach-mark trigger

- **WHEN** a user is in onboarding (`isOnboarding === true`)
- **AND** either the user has followed 5 or more artists, OR the live `artistsWithConcertsCount` >= 3
- **AND** the coach mark has not yet been shown this session
- **THEN** the system SHALL activate a coach mark spotlight on the Dashboard nav icon via `CoachMarkService`
- **AND** the trigger SHALL be evaluated from live follow/concert counts in `DiscoveryRoute`, not from a mirrored count cache
- **AND** the user MAY tap the Dashboard icon at any time (with or without the spotlight) to navigate to `/dashboard`
- **AND** tapping the Dashboard icon SHALL navigate only and SHALL NOT advance any onboarding step

#### Scenario: Coach Mark does not reappear

- **WHEN** the coach mark has already been shown for the current onboarding session
- **THEN** the system SHALL NOT display it again even if the user follows more artists

#### Scenario: Pre-seeded follows on page reload

- **WHEN** the discovery page loads during onboarding
- **THEN** the system SHALL hydrate follows from `FollowStore.guestFollows` into the active follow list
- **AND** the system SHALL initiate a concert search via `ConcertService` for any artists not yet tracked

#### Scenario: Snack notification on concert found

- **WHEN** a followed artist's search completes with status `completed`
- **AND** `listConcerts(artistId)` returns at least one concert
- **THEN** the system SHALL display a snack notification indicating the artist has upcoming events

### Requirement: Single-Flag Onboarding State

The system SHALL model onboarding state as a single persisted boolean rather than an ordered step machine. `OnboardingService` SHALL expose `isOnboarding` as the primary getter and SHALL retain `isCompleted` as its negation (`isCompleted === !isOnboarding`) for call-site compatibility. The persisted value SHALL use completed-polarity (`onboardingComplete`; an absent key means `false`, i.e. still onboarding) so a brand-new user defaults to `isOnboarding === true`. Completion SHALL be a one-way latch exposed as a single `finish()` mutator; once `isOnboarding` becomes `false` it SHALL NOT return to `true` except via an explicit fresh-onboarding reset. The service SHALL NOT expose step values, step ordering, route maps, or a `readyForDashboard` predicate.

#### Scenario: Brand-new user defaults to onboarding

- **WHEN** a user opens the app for the first time and no onboarding key exists in localStorage
- **THEN** `OnboardingService.isOnboarding` SHALL be `true`
- **AND** `OnboardingService.isCompleted` SHALL be `false`

#### Scenario: Completion latches on first meaningful dashboard arrival

- **WHEN** an unauthenticated guest reaches the dashboard for the first time
- **AND** the timetable is real (region is set and concert data has loaded)
- **AND** the guest has at least one followed artist (`followedCount >= 1`)
- **THEN** the system SHALL call `finish()` so `isOnboarding` becomes `false`
- **AND** the latch SHALL be evaluated after the light-celebration decision (so `maybeCelebrate()` observed `isOnboarding === true`), honoring the `needsRegion` deferral

#### Scenario: Latch is independent of whether the celebration is shown

- **WHEN** a guest reaches a meaningful first dashboard (region set, data loaded, `followedCount >= 1`)
- **AND** the light celebration is suppressed (e.g. `localStorage['onboarding.celebrationShown'] === '1'` from a prior session, or `maybeCelebrate()` otherwise early-returns)
- **THEN** the system SHALL still call `finish()`
- **AND** the latch SHALL NOT be gated on the celebration overlay actually rendering

#### Scenario: No latch for a zero-follow dashboard arrival

- **WHEN** an unauthenticated guest with zero followed artists lands on the dashboard (e.g. via deep link, served the empty-state CTA)
- **THEN** the system SHALL NOT call `finish()`
- **AND** `isOnboarding` SHALL remain `true` so the discovery coach mark and page-help auto-open still apply until the guest follows an artist or signs up

#### Scenario: Completion latches on sign-up

- **WHEN** a user completes sign-up via the auth callback
- **THEN** the system SHALL call `finish()` so `isOnboarding` becomes `false`
- **AND** the call SHALL be idempotent if onboarding was already completed

#### Scenario: Completion is one-way

- **WHEN** `isOnboarding` is already `false`
- **AND** the user revisits the dashboard or any onboarding-relevant surface
- **THEN** the system SHALL keep `isOnboarding === false`

#### Scenario: Legacy step value migration

- **WHEN** `OnboardingService` is constructed
- **AND** the legacy `localStorage['onboardingStep']` key exists
- **THEN** the system SHALL set `onboardingComplete = true` when the legacy value denotes completion — i.e. it is in the completed set `{'completed', '7'}` (the legacy numeric index `'7'` mapped to `COMPLETED`)
- **AND** the system SHALL set `onboardingComplete = false` for any other legacy value (e.g. `'discovery'`, `'my-artists'`, `'detail'`)
- **AND** the system SHALL persist the new value and delete the legacy `onboardingStep` key
- **AND** the migration SHALL run at most once per client

### Requirement: Final onboarding step is a non-blocking analytics transparency notice
The onboarding flow SHALL present a one-time **analytics transparency notice** as its final step, rather than an opt-in consent gate. Because analytics runs under the EU-adequacy opt-out model (see the `analytics-consent` capability), there is no signup decision to collect; the notice exists to satisfy the APPI purpose-of-use notification obligation in-context and to signal where the user can opt out. The notice SHALL name PostHog (Klant Solutions B.V., Netherlands) and the cross-border purpose, SHALL link to the privacy policy and to the settings opt-out, and SHALL NOT block progression or alter the default-on analytics state. It SHALL be shown at most once and SHALL NOT reappear once acknowledged.

This requirement replaces the previously-planned signup consent screen with two opt-in toggles; that design is superseded by the opt-out model and is not implemented.

#### Scenario: New user sees the transparency notice once and proceeds
- **WHEN** a user reaches the final onboarding step for the first time
- **THEN** the application SHALL render a transparency notice naming PostHog and the cross-border purpose
- **AND** the notice SHALL link to the privacy policy and to the settings opt-out control
- **AND** dismissing or acknowledging the notice SHALL advance to the authenticated experience without changing the default-on analytics state

#### Scenario: Notice does not gate analytics or block onboarding
- **WHEN** the transparency notice is displayed
- **THEN** identified analytics SHALL already be enabled by default (the notice is informational, not a gate)
- **AND** the application SHALL NOT require any affirmative action on the notice before proceeding
- **AND** the application SHALL NOT show the notice again on subsequent sessions once acknowledged

#### Scenario: Opt-out remains reachable after the notice
- **WHEN** a user who saw the notice later wants to stop analytics
- **THEN** the user SHALL be able to reach the analytics opt-out from the settings page without re-onboarding

