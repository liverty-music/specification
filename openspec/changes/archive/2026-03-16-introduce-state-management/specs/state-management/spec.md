## ADDED Requirements

### Requirement: AppState type definition

The system SHALL define a single `AppState` interface as the Store's state shape, containing `onboarding` and `guestArtists` slices.

#### Scenario: AppState structure

- **WHEN** the `AppState` interface is defined
- **THEN** it SHALL contain an `onboarding` object with `step` (OnboardingStep enum), `spotlightTarget` (string | null), `spotlightMessage` (string | null), `spotlightRadius` (number), and `spotlightActive` (boolean)
- **AND** it SHALL contain a `guestArtists` object with `follows` (GuestFollow array) and `home` (string | null)

### Requirement: Action type definition

The system SHALL define all state mutations as a discriminated union `AppAction` type, ensuring type-safe dispatch.

#### Scenario: Onboarding actions

- **WHEN** the `AppAction` type is defined
- **THEN** it SHALL include `onboarding/advance` (with `step` payload), `onboarding/setSpotlight` (with `target`, `message`, optional `radius`), `onboarding/clearSpotlight`, `onboarding/complete`, and `onboarding/reset`

#### Scenario: Guest artist actions

- **WHEN** the `AppAction` type is defined
- **THEN** it SHALL include `guest/follow` (with `artistId`, `name`), `guest/unfollow` (with `artistId`), `guest/setUserHome` (with `code`), and `guest/clearAll`

### Requirement: Reducer as pure function

The system SHALL implement a single `appReducer` function that returns a new state for each action, without side effects.

#### Scenario: Reducer handles onboarding/advance

- **WHEN** `onboarding/advance` is dispatched with a step value
- **THEN** the reducer SHALL return a new state with `onboarding.step` set to the given value
- **AND** the original state SHALL NOT be mutated

#### Scenario: Reducer handles guest/follow

- **WHEN** `guest/follow` is dispatched with an `artistId` and `name`
- **THEN** the reducer SHALL return a new state with the artist appended to `guestArtists.follows`
- **AND** if the `artistId` already exists in `follows`, the reducer SHALL NOT add a duplicate

#### Scenario: Reducer handles guest/unfollow

- **WHEN** `guest/unfollow` is dispatched with an `artistId`
- **THEN** the reducer SHALL return a new state with the artist removed from `guestArtists.follows`

#### Scenario: Reducer handles guest/setUserHome

- **WHEN** `guest/setUserHome` is dispatched with a `code`
- **THEN** the reducer SHALL return a new state with `guestArtists.home` set to the given code

#### Scenario: Reducer handles guest/clearAll

- **WHEN** `guest/clearAll` is dispatched
- **THEN** the reducer SHALL return a new state with `guestArtists.follows` as an empty array and `guestArtists.home` as null

#### Scenario: Reducer handles onboarding/setSpotlight

- **WHEN** `onboarding/setSpotlight` is dispatched with `target`, `message`, and optional `radius`
- **THEN** the reducer SHALL return a new state with `spotlightTarget`, `spotlightMessage`, `spotlightRadius` (default 40 if not provided), and `spotlightActive` set to true

#### Scenario: Reducer handles onboarding/clearSpotlight

- **WHEN** `onboarding/clearSpotlight` is dispatched
- **THEN** the reducer SHALL return a new state with `spotlightTarget` and `spotlightMessage` set to null and `spotlightActive` set to false

#### Scenario: Reducer handles onboarding/complete

- **WHEN** `onboarding/complete` is dispatched
- **THEN** the reducer SHALL return a new state with `onboarding.step` set to COMPLETED and spotlight cleared

#### Scenario: Reducer handles onboarding/reset

- **WHEN** `onboarding/reset` is dispatched
- **THEN** the reducer SHALL return a new state with `onboarding` reset to initial values (step = LP, spotlight inactive)

#### Scenario: Unknown action passthrough

- **WHEN** an unrecognized action type is dispatched
- **THEN** the reducer SHALL return the current state unchanged

### Requirement: Store registration

The system SHALL register `@aurelia/state` via `StateDefaultConfiguration.init()` in `main.ts`, providing the initial state, reducer, and middleware configuration.

#### Scenario: Store initialization with persisted state

- **WHEN** the application starts
- **THEN** the system SHALL load persisted state from localStorage
- **AND** merge it with the default initial state
- **AND** register the Store with the merged state and `appReducer`

### Requirement: Persistence middleware

The system SHALL implement an `After` middleware that persists relevant state slices to localStorage after each dispatch.

#### Scenario: Onboarding step persisted

- **WHEN** any action changes `onboarding.step`
- **THEN** the middleware SHALL write the new step value to localStorage under the onboarding step key

#### Scenario: Guest follows persisted

- **WHEN** any action changes `guestArtists.follows`
- **THEN** the middleware SHALL write the updated follows array to localStorage under the guest followed artists key

#### Scenario: Guest home persisted

- **WHEN** any action changes `guestArtists.home`
- **THEN** the middleware SHALL write the updated home value to localStorage under the guest home key

### Requirement: Logging middleware (development only)

The system SHALL implement a `Before` middleware that logs dispatched actions and current state in development mode.

#### Scenario: Action logged in development

- **WHEN** an action is dispatched in development mode
- **THEN** the middleware SHALL log the action type and payload to the console
- **AND** the middleware SHALL NOT log in production builds
