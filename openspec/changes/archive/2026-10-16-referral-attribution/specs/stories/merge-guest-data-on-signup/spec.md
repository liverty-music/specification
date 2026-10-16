## MODIFIED Requirements

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
  per-account receipt (e.g. `guestMerged:<userId>`), then clear the
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
follow store SHALL clear `guest.followedArtists` as part of this cleanup. Partial failures SHALL be healed by boot reconciliation (see the
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
- **AND** the artist whose hype failed SHALL stay in `guest.followedArtists`, so
  boot reconciliation retries it on the next authenticated start and the hype
  is not lost

#### Scenario: Guest data cleared after merge

- **WHEN** the data merge completes
- **THEN** the system SHALL remove `guest.followedArtists` from localStorage as part of the standard guest data cleanup

#### Scenario: Successful data merge

- **WHEN** authentication completes successfully for a guest who has onboarding data
- **THEN** the system SHALL call `UserService.Create` with the
  user's email, home, and preferred language (home/language read from the
  guest's stored preferences); for a returning sign-in `Create` returns the
  existing account unchanged
- **AND** on sign-up the system SHALL switch to the authenticated entity and
  clear its own guest home/language localStorage
- **AND** on a returning sign-in the system SHALL also switch to the
  authenticated entity and clear its own guest home/language localStorage — guest
  preferences are discarded, the existing account's saved values win
- **AND** on **every** successful authentication (sign-up AND returning sign-in)
  the system SHALL publish a `GuestMigrationRequested` event
- **AND** the follow store SHALL call `FollowService.Follow` (and `FollowService.SetHype` for
  non-default hype) for each artist in `guest.followedArtists`, then clear its
  own guest follow localStorage on success

#### Scenario: Identity already has an account

- **WHEN** a guest signs in with an identity that already has an account
- **THEN** `UserService.Get` finds that account, `UserService.Create` is not
  called, and the follow migration continues
- **AND** the guest-chosen home and preferred language SHALL NOT be applied to
  the pre-existing account — the returning user's saved account preferences win
  (only follows merge, as they are additive)

#### Scenario: Guest follow at the default level does not overwrite the account's level

- **WHEN** the account already follows an artist at Away and the guest followed
  the same artist at the default Nearby
- **THEN** after the merge the account still follows the artist at Away
- **AND** a guest's explicit choice of Nearby cannot be told apart from the
  default and is treated the same (known limitation)
- **AND** follows the account stored before the default became Nearby keep
  their stored level

#### Scenario: Follow call fails during merge

- **WHEN** any `FollowService.Follow` or `FollowService.SetHype` call fails during migration
- **THEN** the system SHALL log the error
- **AND** the system SHALL continue with remaining calls (best-effort)
- **AND** the system SHALL still mark onboarding complete (`onboardingComplete`)
- **AND** each artist SHALL be removed from `guest.followedArtists` as its
  `Follow` succeeds, so only the failed items remain in localStorage for boot
  reconciliation to retry idempotently on the next authenticated start

#### Scenario: Merge progress indication

- **WHEN** sign-up is in progress
- **THEN** the system SHALL display a loading indicator on the sign-in callback
  screen
- **AND** the system SHALL NOT navigate away until **user creation** completes
  (the awaited Create call)
- **AND** the system SHALL NOT block navigation on follow migration, which runs
  in the background via `GuestMigrationRequested` (best-effort); failed items are
  healed by boot reconciliation rather than retried in-flight
