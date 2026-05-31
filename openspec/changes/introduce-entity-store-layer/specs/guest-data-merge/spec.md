## MODIFIED Requirements

### Requirement: Data Merge on Authentication

The system SHALL sync locally stored guest data to the backend after successful
authentication, using a per-store, event-driven transition with no central
orchestrator. Home and language SHALL be migrated as Create-time inputs; follows
and hype SHALL be migrated by the follow store after the user exists. Each store
SHALL clear its own guest data when its own migration completes. Partial
failures SHALL be healed by boot reconciliation (see the `entity-store-layer`
capability), not by an in-flight retry barrier.

#### Scenario: Successful data merge

- **WHEN** authentication completes successfully for a guest who has onboarding data
- **THEN** the system SHALL call `UserService.Create` with the user's email,
  home, and preferred language (home/language read from `UserStore`'s guest view)
- **AND** `UserStore` SHALL switch to the authenticated entity and clear its own
  guest home/language localStorage
- **AND** upon user creation the system SHALL publish a `UserCreated` event
- **AND** the follow store SHALL call `ArtistService.Follow` (and `SetHype` for
  non-default hype) for each artist in `guest.followedArtists`, then clear its
  own guest follow localStorage on success

#### Scenario: User already exists during merge

- **WHEN** `UserService.Create` returns `ALREADY_EXISTS`
- **THEN** the system SHALL treat this as success and continue with the follow
  migration

#### Scenario: Follow call fails during merge

- **WHEN** any `ArtistService.Follow` or `SetHype` call fails during migration
- **THEN** the system SHALL log the error
- **AND** the system SHALL continue with remaining calls (best-effort)
- **AND** the system SHALL still set `onboardingStep` to COMPLETED
- **AND** the leftover guest follow data SHALL remain in localStorage for boot
  reconciliation to retry idempotently on the next authenticated start

#### Scenario: Merge progress indication

- **WHEN** the data merge is in progress
- **THEN** the system SHALL display a loading indicator on the SignUp modal
- **AND** the system SHALL NOT navigate away until the merge completes or all retries are exhausted

### Requirement: Guest Data Cleanup

The system SHALL remove guest data from LocalStorage after a successful
migration or when the user starts a fresh tutorial. Each store SHALL clear its
own guest data; sign-out clearing SHALL be triggered by the `SignedOut` event
and SHALL be idempotent and order-independent across stores.

#### Scenario: Cleanup after successful migration

- **WHEN** a store's migration completes successfully
- **THEN** that store SHALL remove its own guest keys from LocalStorage
  (`UserStore`: `guest.home` and the anonymous-period `language` key;
  follow store: `guest.followedArtists`)

#### Scenario: Cleanup on sign-out

- **WHEN** the user signs out
- **THEN** a `SignedOut` event SHALL be published
- **AND** each store SHALL clear its own state idempotently, independent of order

#### Scenario: Cleanup on fresh tutorial start

- **WHEN** a user taps [Get Started] on the LP to begin the tutorial
- **AND** stale guest keys exist in LocalStorage
- **THEN** the system SHALL clear those keys before starting Step 1
