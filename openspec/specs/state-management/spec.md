### Requirement: OnboardingService as singleton state owner

The system SHALL provide an `OnboardingService` registered as `@singleton` via `DI.createInterface<IOnboardingService>()` that owns all onboarding state. Only properties requiring persistence side-effects (`step`) SHALL use `@observable`. Spotlight properties (`spotlightTarget`, `spotlightMessage`, `spotlightRadius`, `spotlightActive`) SHALL be plain class properties — Aurelia's template binding observes them automatically without `@observable`.

#### Scenario: Step property is observable

- **WHEN** `OnboardingService.step` is changed via `setStep()`
- **THEN** Aurelia templates bound to `onboarding.step` SHALL update automatically without dispatch or getState

#### Scenario: Spotlight properties are plain

- **WHEN** `activateSpotlight()` is called
- **THEN** `spotlightTarget`, `spotlightMessage`, `spotlightRadius`, and `spotlightActive` SHALL update and be reflected in bound templates
- **AND** these properties SHALL NOT use `@observable` (no persistence side-effects needed)

#### Scenario: Callback properties preserved

- **WHEN** `OnboardingService` is instantiated
- **THEN** it SHALL expose `onSpotlightTap` and `onBringToFront` callback properties as plain instance properties (not observable)

### Requirement: GuestService as singleton state owner

The system SHALL provide a `GuestService` registered as `@singleton` via `DI.createInterface<IGuestService>()` that owns all guest state: `follows` (GuestFollow array) and `home` (string | null). It SHALL also expose `followedCount` getter and `listFollowed()` method for consumers. The legacy `getHome()` method SHALL be removed — consumers access `home` as a public property directly.

#### Scenario: Follow an artist

- **WHEN** `follow(artist)` is called with an artist not already in `follows`
- **THEN** the artist SHALL be appended to `follows` via `push()` as a `GuestFollow` with `home: null`
- **AND** templates using `repeat.for` over `follows` SHALL update

#### Scenario: Follow duplicate artist

- **WHEN** `follow(artist)` is called with an artist whose `id` already exists in `follows`
- **THEN** `follows` SHALL remain unchanged

#### Scenario: Unfollow an artist

- **WHEN** `unfollow(id)` is called
- **THEN** the matching entry SHALL be removed from `follows` via `splice()`

#### Scenario: Set user home

- **WHEN** `setHome(code)` is called
- **THEN** `home` SHALL be set to the given ISO 3166-2 code

#### Scenario: Clear all guest data

- **WHEN** `clearAll()` is called
- **THEN** `follows` SHALL be cleared via `splice(0)` (same array reference) and `home` set to null

#### Scenario: followedCount getter

- **WHEN** `followedCount` is accessed
- **THEN** it SHALL return `follows.length`

#### Scenario: listFollowed projection

- **WHEN** `listFollowed()` is called
- **THEN** it SHALL return an array of `{ id, name }` objects projected from the current `follows` array

#### Scenario: Home accessed as property

- **WHEN** a consumer needs the guest home value
- **THEN** it SHALL access `guestService.home` directly as a public property
- **AND** no `getHome()` method SHALL exist

### Requirement: GuestFollow type in entities

The system SHALL define `GuestFollow` as an interface in `src/entities/` containing `artist: Artist` and `home: string | null`.

#### Scenario: GuestFollow structure

- **WHEN** `GuestFollow` is imported
- **THEN** it SHALL have an `artist` field of type `Artist` and a `home` field of type `string | null`

### Requirement: Service-level persistence via propertyChanged

Each service SHALL persist its own state to localStorage using `@observable` `propertyChanged` callbacks (for scalar properties) or explicit persistence calls after array mutation. The system SHALL use these localStorage keys: `onboardingStep`, `guest.followedArtists`, `guest.home`.

#### Scenario: Onboarding step persisted on change

- **WHEN** `OnboardingService.step` changes (after initial hydration)
- **THEN** `stepChanged()` SHALL write the new step value to localStorage key `onboardingStep`

#### Scenario: Guest follows persisted after mutation

- **WHEN** `follows` array is mutated via `follow()`, `unfollow()`, or `clearAll()`
- **THEN** the service SHALL call `saveFollows()` from `adapter/storage/guest-storage.ts` to persist the current array

#### Scenario: Guest home persisted on change

- **WHEN** `GuestService.home` changes (after initial hydration)
- **THEN** `homeChanged()` SHALL write to localStorage key `guest.home`, or remove the key if null

### Requirement: Service hydration from localStorage

Each service SHALL hydrate its initial state from localStorage at field initialization time. Hydrated values SHALL be assigned directly in field initializers (e.g., `@observable step = loadStep()`) so that `propertyChanged` callbacks do NOT fire during hydration.

#### Scenario: OnboardingService hydrates step

- **WHEN** `OnboardingService` is instantiated
- **THEN** the `step` field initializer SHALL call `loadStep()` which reads `onboardingStep` from localStorage and returns the stored value if valid, or `'lp'` if missing/invalid

#### Scenario: GuestService hydrates follows and home

- **WHEN** `GuestService` is instantiated
- **THEN** the `follows` field initializer SHALL call `loadFollows()` and the `home` field initializer SHALL call `loadHome()` from `adapter/storage/guest-storage.ts`

#### Scenario: No spurious persistence on hydration

- **WHEN** services are instantiated with persisted state
- **THEN** `stepChanged()` and `homeChanged()` SHALL NOT fire during field initialization
- **AND** no redundant localStorage writes SHALL occur

#### Scenario: Invalid or unrecognized step in localStorage

- **WHEN** `OnboardingService` is instantiated and localStorage contains an unrecognized step value
- **THEN** it SHALL fall back to `'lp'` and overwrite localStorage

### Requirement: Simplified guest-storage POJO-only serialization

The `adapter/storage/guest-storage.ts` module SHALL serialize and deserialize `GuestFollow[]` as plain JSON without legacy format support.

#### Scenario: Save follows

- **WHEN** `saveFollows(follows)` is called
- **THEN** it SHALL write `JSON.stringify(follows)` to localStorage key `guest.followedArtists`

#### Scenario: Load follows with valid data

- **WHEN** `loadFollows()` is called and localStorage contains a valid JSON array of `GuestFollow` objects
- **THEN** it SHALL return the parsed array

#### Scenario: Load follows with invalid data

- **WHEN** `loadFollows()` is called and localStorage contains invalid JSON or a non-array value
- **THEN** it SHALL return an empty array

#### Scenario: No legacy format support

- **WHEN** localStorage contains data in VO-wrapped format (`{ id: { value: "..." } }`), flat `artistId` format, or snake_case fanart fields
- **THEN** `loadFollows()` SHALL NOT attempt to parse these formats and SHALL return entries only if they match the current POJO structure

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

### Requirement: FollowServiceClient as follow state SSoT

The `FollowServiceClient` singleton SHALL own `followedArtists: Artist[]` as `@observable` state, serving as the single source of truth for followed artists across all pages. It SHALL expose `followedIds` (derived `ReadonlySet<string>`) and `followedCount` (derived `number`) getters. For guest users, mutations delegate to `GuestService` for localStorage persistence. For authenticated users, mutations call the backend RPC.

#### Scenario: Hydrate from guest state

- **WHEN** `FollowServiceClient` is asked to hydrate during onboarding
- **THEN** it SHALL set `followedArtists` from `GuestService.follows` mapped to `Artist[]`
- **AND** Aurelia templates bound to `followService.followedCount` SHALL update automatically

#### Scenario: Follow an artist (guest)

- **WHEN** `follow(artist)` is called and the user is not authenticated
- **THEN** the system SHALL optimistically append the artist to `followedArtists`
- **AND** the system SHALL call `GuestService.follow(artist)` for localStorage persistence
- **AND** `followedIds` and `followedCount` SHALL reflect the new state immediately

#### Scenario: Follow an artist (authenticated)

- **WHEN** `follow(artist)` is called and the user is authenticated
- **THEN** the system SHALL optimistically append the artist to `followedArtists`
- **AND** the system SHALL call the backend Follow RPC
- **AND** on RPC failure, the system SHALL rollback `followedArtists` to its previous state

#### Scenario: Duplicate follow is no-op

- **WHEN** `follow(artist)` is called with an artist whose `id` is already in `followedIds`
- **THEN** `followedArtists` SHALL remain unchanged

#### Scenario: followedIds derivation

- **WHEN** `followedIds` is accessed
- **THEN** it SHALL return a `ReadonlySet<string>` derived from current `followedArtists` IDs

### Requirement: ConcertServiceClient concert search and tracking

The `ConcertServiceClient` singleton SHALL provide a `searchAndTrack(artistId, signal, targetCount, onConcertFound?)` method that encapsulates the full search lifecycle: initiate backend search, poll for completion, verify concerts on completion, and accumulate results in `artistsWithConcerts`. The service SHALL own `@observable artistsWithConcerts: Set<string>` tracking which artists have confirmed concerts.

#### Scenario: searchAndTrack initiates backend search

- **WHEN** `searchAndTrack(artistId)` is called
- **AND** the artist is not already tracked
- **THEN** the system SHALL call `searchNewConcerts(artistId)` fire-and-forget
- **AND** the system SHALL start polling via `setInterval` (2000ms) if not already running

#### Scenario: searchAndTrack for already-tracked artist is no-op

- **WHEN** `searchAndTrack(artistId)` is called for an artist already in the tracking map
- **THEN** the system SHALL NOT initiate a new search or duplicate the tracking entry

#### Scenario: Poll detects search completion

- **WHEN** `listSearchStatuses` returns `completed` for an artist
- **THEN** the system SHALL call `listConcerts(artistId)`
- **AND** if concerts exist, the system SHALL add `artistId` to `artistsWithConcerts`
- **AND** if an `onConcertFound` callback was provided, the system SHALL invoke it with the artist ID

#### Scenario: Poll detects search failure

- **WHEN** `listSearchStatuses` returns `failed` for an artist
- **THEN** the system SHALL mark the artist as done without checking concerts

#### Scenario: Per-artist timeout

- **WHEN** an artist's search has been pending for >= 15 seconds
- **THEN** the system SHALL mark the artist as done (timeout)

#### Scenario: Early polling stop at target

- **WHEN** `artistsWithConcerts.size` reaches the provided target count
- **THEN** the system SHALL stop polling immediately via `clearInterval`

#### Scenario: All searches complete stops polling

- **WHEN** all tracked artists have status `done`
- **AND** `artistsWithConcerts.size` has not yet reached the target
- **THEN** the system SHALL stop polling

#### Scenario: AbortSignal cancels polling

- **WHEN** the provided `AbortSignal` is aborted (e.g., page navigation)
- **THEN** the system SHALL stop polling via `clearInterval`
- **AND** the system SHALL retain `artistsWithConcerts` state (not clear it)

#### Scenario: artistsWithConcertsCount getter

- **WHEN** `artistsWithConcertsCount` is accessed
- **THEN** it SHALL return `artistsWithConcerts.size`

### Requirement: Single DI access path

All routes and components SHALL access onboarding and guest state exclusively through `resolve(IOnboardingService)` and `resolve(IGuestService)`. Direct store resolution (`resolveStore()`, `resolve(IStore)`) SHALL NOT exist in the codebase.

#### Scenario: No direct store access

- **WHEN** the codebase is searched for `resolveStore`, `IStore`, or `@aurelia/state` imports
- **THEN** zero results SHALL be found outside of test files
