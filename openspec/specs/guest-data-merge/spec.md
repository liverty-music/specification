# guest-data-merge Specification

## Purpose

Defines how guest session data captured during onboarding (followed artists with hype, region) is stored locally and merged to the backend via existing RPCs upon successful authentication, then cleaned up.

## Requirements

### Requirement: Guest Data Storage

The system SHALL store guest session data in LocalStorage under namespaced keys during the onboarding tutorial. Guest follows SHALL be stored as `FollowedArtist[]` including hype level, under a single key.

#### Scenario: Followed artists stored locally with hype

- **WHEN** a guest user taps an artist bubble during Artist Discovery
- **THEN** the system SHALL append `{ artist, hype: DEFAULT_HYPE }` to a JSON array in LocalStorage under `guest.followedArtists`

#### Scenario: Hype update stored inline in follow entry

- **WHEN** a guest user changes a hype level for a followed artist
- **THEN** the system SHALL update the `hype` field of the matching entry in `guest.followedArtists`
- **AND** the system SHALL NOT write to the `liverty:guest:hypes` key

#### Scenario: Legacy data read with hype fallback

- **WHEN** `guest.followedArtists` contains entries in the old `GuestFollow` format (missing `hype` field)
- **THEN** the system SHALL accept those entries and assign `DEFAULT_HYPE` as the hype value
- **AND** the system SHALL NOT throw or discard those entries

#### Scenario: Home area selection stored locally

- **WHEN** a guest user selects a home area during Step 3 (Dashboard)
- **THEN** the system SHALL store the selected value in LocalStorage under `guest.home` (owned by `UserStore`), so the existing per-store cleanup covers it

### Requirement: Guest hype included in data merge on signup

The system SHALL merge guest hype values to the backend on signup by reading hype from the unified `guest.followedArtists` entries.

#### Scenario: Guest hype merged from follow entries

- **WHEN** Passkey authentication completes successfully
- **AND** `guest.followedArtists` contains entries with `hype !== DEFAULT_HYPE`
- **THEN** the system SHALL call `FollowService.SetHype` for each such artist as part of the merge sequence
- **AND** hype merge SHALL occur after artist follow calls complete

#### Scenario: Hype merge failure is non-blocking

- **WHEN** a `FollowService.SetHype` call fails during merge
- **THEN** the system SHALL log the error
- **AND** the system SHALL continue with remaining hype calls (best-effort)
- **AND** the merge SHALL still be considered complete

#### Scenario: Guest data cleared after merge

- **WHEN** the data merge completes
- **THEN** the system SHALL remove `guest.followedArtists` from localStorage as part of the standard guest data cleanup
- **AND** the system SHALL NOT need to remove `liverty:guest:hypes` (key is no longer written)

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
- **THEN** **on sign-up** the system SHALL call `UserService.Create` with the
  user's email, home, and preferred language (home/language read from
  `UserStore`'s guest view) — a returning sign-in skips `Create` because the
  account already exists
- **AND** on sign-up `UserStore` SHALL switch to the authenticated entity and
  clear its own guest home/language localStorage
- **AND** on a returning sign-in `UserStore` SHALL also switch to the
  authenticated entity (via `ensureLoaded`, no `Create` call) and clear its own
  guest home/language localStorage — guest preferences are discarded, the
  existing account's saved values win
- **AND** on **every** successful authentication (sign-up AND returning sign-in)
  the system SHALL publish a `GuestMigrationRequested` event
- **AND** the follow store SHALL call `ArtistService.Follow` (and `SetHype` for
  non-default hype) for each artist in `guest.followedArtists`, then clear its
  own guest follow localStorage on success

#### Scenario: User already exists during merge

- **WHEN** `UserService.Create` returns `ALREADY_EXISTS`
- **THEN** the system SHALL treat this as success and continue with the follow
  migration
- **AND** the guest-chosen home and preferred language SHALL NOT be applied to
  the pre-existing account — the returning user's saved account preferences win
  (only follows merge, as they are additive)

#### Scenario: Follow call fails during merge

- **WHEN** any `ArtistService.Follow` or `SetHype` call fails during migration
- **THEN** the system SHALL log the error
- **AND** the system SHALL continue with remaining calls (best-effort)
- **AND** the system SHALL still set `onboardingStep` to COMPLETED
- **AND** each artist SHALL be removed from `guest.followedArtists` as its
  `Follow` succeeds, so only the failed items remain in localStorage for boot
  reconciliation to retry idempotently on the next authenticated start

#### Scenario: Merge progress indication

- **WHEN** sign-up is in progress
- **THEN** the system SHALL display a loading indicator on the SignUp modal
- **AND** the system SHALL NOT navigate away until **user creation** completes
  (the awaited Create call)
- **AND** the system SHALL NOT block navigation on follow migration, which runs
  in the background via `GuestMigrationRequested` (best-effort); failed items are
  healed by boot reconciliation rather than retried in-flight

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

