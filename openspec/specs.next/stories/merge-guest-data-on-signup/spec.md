# Merge guest data on signup

## Purpose

Ensures artist follows, hype levels, and region preferences a guest accumulates before creating an account are stored locally, then merged into the new account on successful sign-up and cleared afterward, with reconciliation if a merge was interrupted.

## Requirements

### Requirement: Event-Driven Auth-Boundary Transitions

Guest→authenticated transition and sign-out SHALL be handled per-store via
domain events, with no central orchestrator and no cross-store completion
barrier. Each store SHALL clear its own guest data when its own migration
completes.

#### Scenario: Home and language migrate as Create-time inputs
- **WHEN** a guest signs up
- **THEN** the sign-up flow SHALL read home and language from the user
  store's guest view and pass them to the user-create call as inputs
- **AND** the user store SHALL persist them, switch its current user to the
  authenticated entity, and clear its own guest localStorage for those fields
- **AND** no post-creation event SHALL be required to migrate home or language

#### Scenario: Follows migrate after a guest authenticates
- **WHEN** a guest authenticates (sign-up OR returning sign-in)
- **THEN** a `GuestMigrationRequested` event SHALL be published on every
  successful authentication (not gated on sign-up), so guest follows are not
  lost when a returning user signs in
- **AND** the follow store SHALL migrate guest follows and hype to the backend
  using idempotent calls now that a user id exists (a no-op when the queue is
  empty; the per-account receipt guards against double-migration)
- **AND** the follow store SHALL clear its own guest localStorage on success
- **AND** follow migration SHALL be best-effort (a failed item SHALL be logged
  and SHALL NOT block the remaining items)

#### Scenario: Sign-out clears each store independently
- **WHEN** the user signs out
- **THEN** a `SignedOut` event SHALL be published
- **AND** each store SHALL clear its own state independently
- **AND** clearing SHALL be idempotent and order-independent across stores

#### Scenario: Sign-out evicts user-specific caches
- **WHEN** the user signs out
- **THEN** any store that caches user-specific data (e.g. the follow store's
  followed-artist projections) SHALL evict that cache
- **AND** a subsequent visitor on the same browser SHALL NOT see the previous
  user's cached data
- **AND** cache-only stores holding only non-user-specific public resources
  (e.g. a top-artists list) MAY retain their cache

### Requirement: Boot Reconciliation of Unmerged Guest Data

Each store SHALL reconcile leftover guest data at application start to heal
partial-migration failures, without in-flight retry coordination. A successful
migration SHALL write a persistent per-account **guest-merge receipt**; the
receipt — not the mere presence of guest data — SHALL decide whether a
reconcile migrates, so reverted state is never resurrected.

#### Scenario: Leftover guest data migrated on first authenticated boot
- **WHEN** the application starts
- **AND** the user is authenticated
- **AND** no guest-merge receipt exists for the account
- **AND** a store finds leftover guest data in localStorage
- **THEN** the store SHALL run its idempotent migration, then write the
  per-account receipt (e.g. `liverty:guestMerged:<userId>`), then clear the
  leftover guest data

#### Scenario: Reconciliation does not resurrect reverted state
- **WHEN** the application starts
- **AND** a guest-merge receipt already exists for the account
- **AND** residual guest data is still present (a prior clear failed)
- **THEN** the store SHALL clear the residual guest data WITHOUT re-running the
  migration
- **AND** state the user changed after signup SHALL NOT be resurrected

#### Scenario: Per-item drain for the follow queue
- **WHEN** the follow store migrates the guest follow queue
- **THEN** it SHALL remove each artist from `guest.followedArtists` as that
  artist's `Follow` call succeeds
- **AND** the leftover queue SHALL therefore contain only items that failed
- **AND** a subsequent reconcile SHALL retry only those failed items, never
  re-following an already-migrated artist

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
- **THEN** the system SHALL store the selected value in LocalStorage under `guest.home`, so the existing per-store cleanup covers it

### Requirement: Data Merge on Authentication

The system SHALL sync locally stored guest data to the backend after
successful authentication, using a per-store, event-driven transition with no
central orchestrator. Home and language SHALL be migrated as Create-time
inputs; follows and hype SHALL be migrated by the follow store after the user
exists, reading hype from the unified `guest.followedArtists` entries. Each
store SHALL clear its own guest data when its own migration completes; the
follow store SHALL clear `guest.followedArtists` as part of this cleanup, and
SHALL NOT need to remove `liverty:guest:hypes` (the key is no longer
written). Partial failures SHALL be healed by boot reconciliation (see the
`entity-store-layer` capability), not by an in-flight retry barrier.

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

#### Scenario: Successful data merge

- **WHEN** authentication completes successfully for a guest who has onboarding data
- **THEN** **on sign-up** the system SHALL call `UserService.Create` with the
  user's email, home, and preferred language (home/language read from the
  guest's stored preferences) — a returning sign-in skips `Create` because the
  account already exists
- **AND** on sign-up the system SHALL switch to the authenticated entity and
  clear its own guest home/language localStorage
- **AND** on a returning sign-in the system SHALL also switch to the
  authenticated entity (reusing the existing account-loading behavior, no
  `Create` call) and clear its own guest home/language localStorage — guest
  preferences are discarded, the existing account's saved values win
- **AND** on **every** successful authentication (sign-up AND returning sign-in)
  the system SHALL publish a `GuestMigrationRequested` event
- **AND** the follow store SHALL call `FollowService.Follow` (and `FollowService.SetHype` for
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

- **WHEN** any `FollowService.Follow` or `FollowService.SetHype` call fails during migration
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
  (the user store: `guest.home` and the anonymous-period `language` key;
  the follow store: `guest.followedArtists`)

#### Scenario: Cleanup on sign-out

- **WHEN** the user signs out
- **THEN** a `SignedOut` event SHALL be published
- **AND** each store SHALL clear its own state idempotently, independent of order

#### Scenario: Cleanup on fresh tutorial start

- **WHEN** a user taps [Get Started] on the LP to begin the tutorial
- **AND** stale guest keys exist in LocalStorage
- **THEN** the system SHALL clear those keys before starting Step 1

### Requirement: Guest data accumulates before signup and clears after merge

Guest state SHALL be a simple data bag tracking ephemeral data accumulated before the user creates an account (followed artists and home location). On signup the data is merged into the backend, then cleared. There are no discrete named states, only data mutations. The key invariant is that following an artist as a guest is idempotent — following an artist a second time is a no-op.

| Action                 | Effect                                                  | Origin                 |
|------------------------|-----------------------------------------------------------|-------------------------|
| Follow an artist       | Append `{ artistId, name }` to follows (skip if exists) | the discovery page      |
| Unfollow an artist     | Remove entry by artistId                                | the followed-artists page |
| Set home area          | Set home ISO-3166-2 code                                | the area selector (modal) |
| Clear all guest data   | Reset follows to `[]` and home to `null`                | the welcome page, or after a signup merge |

#### Scenario: guest/follow is idempotent

- **WHEN** following an artist already present in the follows list
- **THEN** the list SHALL be unchanged (no duplicate entry)

#### Scenario: guest/follow appends a new artist

- **WHEN** a new artist is followed from the discovery page
- **THEN** `{ artistId, name }` SHALL be appended to the follows list

#### Scenario: guest/unfollow removes an entry

- **WHEN** an artist present in the list is unfollowed
- **THEN** the matching entry SHALL be removed by `artistId`

#### Scenario: guest/setUserHome sets the home code

- **WHEN** the home area is set from the area selector
- **THEN** the guest home SHALL be set to the given ISO-3166-2 code

#### Scenario: guest/clearAll resets on merge or welcome

- **WHEN** all guest data is cleared (from the welcome page or after a signup merge)
- **THEN** follows SHALL be reset to `[]` and home to `null`
