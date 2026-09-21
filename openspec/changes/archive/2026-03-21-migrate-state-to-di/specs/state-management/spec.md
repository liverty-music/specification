## MODIFIED Requirements

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

The system SHALL persist onboarding step, guest follows, and guest home to localStorage. The previous `After` middleware pattern is replaced by the "Service-level persistence via propertyChanged" requirement (see ADDED). This requirement retains only the contract of WHAT is persisted and under which localStorage keys.

#### Scenario: Persisted keys unchanged

- **WHEN** state is persisted
- **THEN** the system SHALL use the same localStorage keys as before: `onboardingStep`, `guest.followedArtists`, `guest.home`

### Requirement: State hydration from localStorage

The system SHALL hydrate initial state from localStorage, validating string step values. Hydration SHALL occur at field initialization time in each service, replacing the previous `loadPersistedState()` function.

#### Scenario: Valid string step in localStorage

- **WHEN** `OnboardingService` is instantiated and localStorage contains a recognized string step value
- **THEN** the field initializer SHALL set `step` to that value

#### Scenario: Invalid or unrecognized step in localStorage

- **WHEN** `OnboardingService` is instantiated and localStorage contains an unrecognized step value
- **THEN** it SHALL fall back to `'lp'` and overwrite localStorage

## REMOVED Requirements

### Requirement: AppState type definition

**Reason**: Replaced by per-service state ownership. Onboarding state lives in `OnboardingService`, guest state in `GuestService`. No unified `AppState` interface is needed.

**Migration**: Delete `src/state/app-state.ts`. Move `GuestFollow` type to `src/entities/`.

### Requirement: Action type definition

**Reason**: Actions are a Redux concept. State mutations are now direct method calls on services.

**Migration**: Delete `src/state/actions.ts`.

### Requirement: Reducer as pure function

**Reason**: The reducer is replaced by service methods that directly mutate `@observable` properties. Business logic (e.g., duplicate follow guard) moves into service methods.

**Migration**: Delete `src/state/reducer.ts`. Port business logic to service methods.

### Requirement: Logging middleware via factory

**Reason**: Logging is handled by each service using `ILogger.scopeTo()` in its methods, as services already do today.

**Migration**: Delete logging middleware from `src/state/middleware.ts`.

### Requirement: Store resolution requires active DI context

**Reason**: `IStore` and `resolveStore()` are removed. Services are resolved via standard `resolve()` which already requires DI context.

**Migration**: Delete `src/state/store-interface.ts`. Replace all `resolveStore()` calls with `resolve(IOnboardingService)` or `resolve(IGuestService)`.
