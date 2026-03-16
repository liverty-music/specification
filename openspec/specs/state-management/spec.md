## MODIFIED Requirements

### Requirement: AppState type definition

The system SHALL define a single `AppState` interface as the Store's state shape, containing `onboarding` and `guest` slices.

#### Scenario: AppState structure

- **WHEN** the `AppState` interface is defined
- **THEN** it SHALL contain an `onboarding` object with `step` (OnboardingStepValue string literal), `spotlightTarget` (string), `spotlightMessage` (string), `spotlightRadius` (string), and `spotlightActive` (boolean)
- **AND** it SHALL contain a `guest` object with `follows` (GuestFollow array) and `home` (string | null)

### Requirement: Action type definition

The system SHALL define all state mutations as a discriminated union `AppAction` type, ensuring type-safe dispatch.

#### Scenario: Onboarding actions

- **WHEN** the `AppAction` type is defined
- **THEN** it SHALL include `onboarding/advance` (with `step` payload), `onboarding/setSpotlight` (with `target`, `message`, optional `radius`), `onboarding/clearSpotlight`, `onboarding/complete`, and `onboarding/reset`

#### Scenario: Guest actions

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

#### Scenario: Unknown action passthrough

- **WHEN** an unrecognized action type is dispatched
- **THEN** the reducer SHALL return the current state unchanged (same reference)

### Requirement: OnboardingStep string values

The system SHALL define `OnboardingStep` as a const object with string literal values representing each step by name.

#### Scenario: Step values

- **WHEN** `OnboardingStep` is defined
- **THEN** it SHALL contain exactly these entries: `LP: 'lp'`, `DISCOVERY: 'discovery'`, `DASHBOARD: 'dashboard'`, `DETAIL: 'detail'`, `MY_ARTISTS: 'my-artists'`, `COMPLETED: 'completed'`
- **AND** it SHALL NOT contain `LOADING` or `SIGNUP`

#### Scenario: Step ordering

- **WHEN** step ordering is needed (e.g., auth-hook route guard)
- **THEN** the system SHALL use an explicit `STEP_ORDER` array to determine step precedence
- **AND** the system SHALL provide a `stepIndex(step)` function that returns the ordinal position

#### Scenario: Onboarding detection

- **WHEN** determining if the user is in the onboarding flow
- **THEN** the system SHALL check membership in an `ONBOARDING_STEPS` Set containing `'discovery'`, `'dashboard'`, `'detail'`, `'my-artists'`
- **AND** the system SHALL NOT use numeric range comparison

### Requirement: Persistence middleware

The system SHALL implement an `After` middleware that persists relevant state slices to localStorage after each dispatch.

#### Scenario: Onboarding step persisted as string

- **WHEN** any action changes `onboarding.step`
- **THEN** the middleware SHALL write the string step value (e.g., `'dashboard'`) to localStorage

#### Scenario: Guest follows persisted

- **WHEN** any action changes `guest.follows`
- **THEN** the middleware SHALL write the updated follows array to localStorage under the guest followed artists key

#### Scenario: Guest home persisted

- **WHEN** any action changes `guest.home`
- **THEN** the middleware SHALL write the updated home value to localStorage, or remove the key if null

### Requirement: Logging middleware via factory

The system SHALL implement a `Before` middleware created via a factory function that accepts Aurelia's `ILogger`.

#### Scenario: Logger factory

- **WHEN** the logging middleware is created
- **THEN** it SHALL accept an `ILogger` instance scoped to `'Store'`
- **AND** it SHALL log the action type using `logger.info()`

#### Scenario: Dev-only registration

- **WHEN** the application starts
- **THEN** the logging middleware SHALL only be registered in the middleware array when `import.meta.env.DEV` is true

### Requirement: State hydration from localStorage

The system SHALL hydrate initial state from localStorage, validating string step values.

#### Scenario: Valid string step in localStorage

- **WHEN** localStorage contains a recognized string step value (e.g., `'dashboard'`)
- **THEN** `loadPersistedState()` SHALL return the state with that step value

#### Scenario: Invalid or unrecognized step in localStorage

- **WHEN** localStorage contains an unrecognized step value
- **THEN** `loadPersistedState()` SHALL fall back to `'lp'` and overwrite localStorage

## REMOVED Requirements

### Requirement: LOADING step

**Reason**: The LOADING step (formerly step 2) was removed in a prior change. Its enum value was kept for backward compatibility which is no longer needed.

**Migration**: Delete `OnboardingStep.LOADING`. Remove backward compat mapping in `loadPersistedState()`.

### Requirement: SIGNUP step

**Reason**: The SIGNUP step (formerly step 6) was removed in a prior change. Its enum value was kept for backward compatibility which is no longer needed.

**Migration**: Delete `OnboardingStep.SIGNUP`. Remove backward compat mapping in `loadPersistedState()`.
