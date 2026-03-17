## MODIFIED Requirements

### Requirement: AppState type definition

The system SHALL define a single `AppState` interface as the Store's state shape, containing `onboarding`, `guest`, and `discovery` slices.

#### Scenario: AppState structure

- **WHEN** the `AppState` interface is defined
- **THEN** it SHALL contain an `onboarding` object with `step` (OnboardingStepValue string literal), `spotlightTarget` (string), `spotlightMessage` (string), `spotlightRadius` (string), and `spotlightActive` (boolean)
- **AND** it SHALL contain a `guest` object with `follows` (GuestFollow array) and `home` (string | null)
- **AND** it SHALL contain a `discovery` object with `followedArtists` (FollowedArtist array)

#### Scenario: FollowedArtist shape

- **WHEN** the `FollowedArtist` interface is defined
- **THEN** it SHALL contain `id` (string), `name` (string), and `mbid` (string)

#### Scenario: Discovery initial state

- **WHEN** the application initializes
- **THEN** `discovery.followedArtists` SHALL be an empty array

### Requirement: Action type definition

The system SHALL define all state mutations as a discriminated union `AppAction` type, ensuring type-safe dispatch.

#### Scenario: Onboarding actions

- **WHEN** the `AppAction` type is defined
- **THEN** it SHALL include `onboarding/advance` (with `step` payload), `onboarding/setSpotlight` (with `target`, `message`, optional `radius`), `onboarding/clearSpotlight`, `onboarding/complete`, and `onboarding/reset`

#### Scenario: Guest actions

- **WHEN** the `AppAction` type is defined
- **THEN** it SHALL include `guest/follow` (with `artistId`, `name`), `guest/unfollow` (with `artistId`), `guest/setUserHome` (with `code`), and `guest/clearAll`

#### Scenario: Discovery actions

- **WHEN** the `AppAction` type is defined
- **THEN** it SHALL include `discovery/follow` (with `artist: FollowedArtist`) and `discovery/unfollow` (with `artistId: string`)

### Requirement: Reducer as pure function

The system SHALL implement a single `appReducer` function that returns a new state for each action, without side effects.

#### Scenario: Reducer handles onboarding/advance

- **WHEN** `onboarding/advance` is dispatched with a step value
- **THEN** the reducer SHALL return a new state with `onboarding.step` set to the given value
- **AND** the original state SHALL NOT be mutated

#### Scenario: Reducer handles guest/follow

- **WHEN** `guest/follow` is dispatched with an `artistId` and `name`
- **THEN** the reducer SHALL return a new state with the artist appended to `guest.follows`
- **AND** if the `artistId` already exists in `follows`, the reducer SHALL return the current state unchanged

#### Scenario: Reducer handles guest/unfollow

- **WHEN** `guest/unfollow` is dispatched with an `artistId`
- **THEN** the reducer SHALL return a new state with the artist removed from `guest.follows`

#### Scenario: Reducer handles guest/setUserHome

- **WHEN** `guest/setUserHome` is dispatched with a `code`
- **THEN** the reducer SHALL return a new state with `guest.home` set to the given code

#### Scenario: Reducer handles guest/clearAll

- **WHEN** `guest/clearAll` is dispatched
- **THEN** the reducer SHALL return a new state with `guest.follows` as an empty array and `guest.home` as null

#### Scenario: Reducer handles onboarding/setSpotlight

- **WHEN** `onboarding/setSpotlight` is dispatched with `target`, `message`, and optional `radius`
- **THEN** the reducer SHALL return a new state with `spotlightTarget`, `spotlightMessage`, `spotlightRadius` (default `'12px'` if not provided), and `spotlightActive` set to true

#### Scenario: Reducer handles onboarding/clearSpotlight

- **WHEN** `onboarding/clearSpotlight` is dispatched
- **THEN** the reducer SHALL return a new state with `spotlightTarget` and `spotlightMessage` set to empty string, `spotlightRadius` reset to `'12px'`, and `spotlightActive` set to false

#### Scenario: Reducer handles onboarding/complete

- **WHEN** `onboarding/complete` is dispatched
- **THEN** the reducer SHALL return a new state with `onboarding.step` set to `'completed'` and spotlight cleared (target/message empty, radius `'12px'`, active false)

#### Scenario: Reducer handles onboarding/reset

- **WHEN** `onboarding/reset` is dispatched
- **THEN** the reducer SHALL return a new state with `onboarding` reset to initial values (step = `'lp'`, spotlight inactive)

#### Scenario: Reducer handles discovery/follow

- **WHEN** `discovery/follow` is dispatched with an `artist` object containing `id`, `name`, and `mbid`
- **THEN** the reducer SHALL return a new state with the artist appended to `discovery.followedArtists`
- **AND** if the `artist.id` already exists in `followedArtists`, the reducer SHALL return the current state unchanged

#### Scenario: Reducer handles discovery/unfollow

- **WHEN** `discovery/unfollow` is dispatched with an `artistId`
- **THEN** the reducer SHALL return a new state with the artist removed from `discovery.followedArtists`

#### Scenario: Unknown action passthrough

- **WHEN** an unrecognized action type is dispatched
- **THEN** the reducer SHALL return the current state unchanged (same reference)
