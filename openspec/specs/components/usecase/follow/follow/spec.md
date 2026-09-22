# Follow

## Purpose

Lets a user follow an artist, recording the relationship with a default hype level and triggering a background concert search for that artist on first follow, without letting search failures block the follow action.

## Requirements

### Requirement: Follow Relationship Data Model

The system SHALL maintain a follow relationship between users and artists, stored in the followed_artists table. The use case layer SHALL resolve the authenticated user's external identity (Zitadel `sub` claim) to the internal user UUID before querying or writing to the `followed_artists` table.

#### Scenario: Passion level stored on follow relationship

- **GIVEN** the followed_artists table
- **WHEN** a follow relationship exists
- **THEN** a passion_level column SHALL store the user's enthusiasm tier (must_go, local_only, keep_an_eye) with a default of local_only

#### Scenario: Successfully following an artist
- **WHEN** a user with a valid Zitadel identity requests to follow an artist with a valid MBID
- **THEN** the system SHALL resolve the Zitadel `sub` claim to the internal user UUID via `UserRepository.GetByExternalID`
- **AND** the system SHALL create a record in the `followed_artists` table linking the internal user UUID to the artist

#### Scenario: User record not found during follow

- **WHEN** `Follow` is called with a valid Zitadel identity but no corresponding user record exists
- **THEN** the system SHALL return `NOT_FOUND` error indicating the user must complete registration first

### Requirement: Trigger concert search on first follow
When a user follows an artist and no search log exists for that artist, the system SHALL launch a background concert search via `SearchNewConcerts`. The frontend SHALL NOT independently call `SearchNewConcerts` after a follow — concert discovery is solely the responsibility of the backend (first-follow trigger) and the daily cronjob.

#### Scenario: First follow triggers search
- **WHEN** a user follows an artist that has no entry in the search log
- **THEN** the system SHALL asynchronously call `SearchNewConcerts(artistID)` in a background goroutine

#### Scenario: Subsequent follow skips search
- **WHEN** a user follows an artist that already has a search log entry
- **THEN** the system SHALL NOT trigger a background search

#### Scenario: Already-following is treated as no-op
- **WHEN** a user follows an artist they already follow (ErrAlreadyExists)
- **THEN** the system SHALL return success without checking the search log or triggering search

#### Scenario: Frontend does not call SearchNewConcerts after follow
- **WHEN** a user follows an artist from the Discovery page
- **THEN** the frontend SHALL NOT call the `SearchNewConcerts` RPC
- **AND** the backend MUST be the sole initiator of concert discovery

### Requirement: Search errors do not affect follow operation
The Follow RPC response SHALL NOT be affected by background search success or failure.

#### Scenario: Search fails silently
- **WHEN** a background search triggered by follow encounters an error
- **THEN** the system SHALL log the error and NOT propagate it to the Follow caller

### Requirement: Search log check failure is non-blocking
The system SHALL treat search log lookup errors (other than NotFound) as non-fatal during follow.

#### Scenario: Search log lookup fails
- **WHEN** `searchLogRepo.GetByArtistID` returns an unexpected error
- **THEN** the system SHALL log the error and skip the background search (do not trigger search on ambiguous state)

### Requirement: Default hype tier for new follows is Nearby

The system SHALL initialize every newly-created follow record with hype value `nearby` (proto enum `HYPE_TYPE_NEARBY`), regardless of whether the follow is created by a guest user (localStorage-backed) or an authenticated user (RPC-backed). The frontend constant `DEFAULT_HYPE` SHALL be set to `'nearby'`.

#### Scenario: Guest follows an artist from Discovery

- **WHEN** a guest user taps an artist bubble on the Discovery page to follow them
- **THEN** the resulting follow record stored in `GuestService` SHALL have `hype: 'nearby'`
- **AND** the artist SHALL appear on the My Artists page with the Nearby dot (third position) visually active

#### Scenario: Authenticated user follows an artist

- **WHEN** an authenticated user follows an artist via the Discovery flow
- **THEN** the follow record stored by the backend (after `Follow` RPC succeeds) SHALL have `hype = HYPE_TYPE_NEARBY`
- **AND** subsequent `ListFollowed` responses SHALL return that artist with the Nearby hype value until the user explicitly changes it

#### Scenario: Guest-data merge respects new default

- **WHEN** a guest user with follows at the default `nearby` value completes signup
- **AND** the guest-data merge service processes those follows
- **THEN** the merge service SHALL still suppress merging follows that match the default value (`nearby`), so that an authenticated user's pre-existing hype setting for the same artist is not overwritten by a guest record that simply held the default

#### Scenario: Explicit guest "Nearby" choice indistinguishable from passive default acceptance (known limitation)

- **WHEN** a guest user deliberately sets a follow's hype to `nearby` (for example by following the artist, changing the tier to `away`, then changing back to `nearby`)
- **AND** the guest later signs up and the guest-data merge service runs
- **THEN** the merge service SHALL apply the same suppression as for passive default acceptance (no SetHype RPC call), because the persisted guest hype value `nearby` carries no marker distinguishing "explicit choice" from "default left untouched"
- **AND** if the authenticated user's backend record for that artist holds a different hype value (legacy `watch` from before the default flip, or a tier set on another device), the guest's explicit `nearby` choice SHALL NOT overwrite it
- **AND** this is an accepted limitation of the current suppression heuristic; resolving it would require either a separate "explicit-set" flag in guest storage or always calling SetHype during merge (which would overwrite legitimate non-default backend values). The trade-off is revisited only if the limitation becomes observably user-visible.

#### Scenario: Existing stored records are not migrated

- **WHEN** the `DEFAULT_HYPE` change ships
- **AND** a user has previously-stored follow records with `hype = 'watch'`
- **THEN** the stored values SHALL remain `'watch'`; only newly-created follows SHALL receive `'nearby'`
- **AND** no database migration or client-side mutation SHALL alter the existing records

### Requirement: Follow an artist

Followed-artist state SHALL be owned by a single observable store, serving as the single source of truth for followed artists across all pages. The store SHALL expose derived views for the set of followed artist IDs and the count of followed artists. For guest users, changes SHALL be persisted to local storage. For authenticated users, changes SHALL be persisted via the backend Follow RPC.

#### Scenario: Hydrate from guest state

- **WHEN** the store is asked to hydrate during onboarding
- **THEN** it SHALL set the followed artists from the guest's locally stored follows
- **AND** any UI bound to the followed-artist count SHALL update automatically

#### Scenario: Follow an artist (guest)

- **WHEN** an artist is followed and the user is not authenticated
- **THEN** the system SHALL optimistically append the artist to the followed artists
- **AND** the system SHALL persist the follow to local storage
- **AND** the derived followed-artist set and count SHALL reflect the new state immediately

#### Scenario: Follow an artist (authenticated)

- **WHEN** an artist is followed and the user is authenticated
- **THEN** the system SHALL optimistically append the artist to the followed artists
- **AND** the system SHALL call the backend Follow RPC
- **AND** on RPC failure, the system SHALL roll back the followed artists to their previous state

#### Scenario: Duplicate follow is no-op

- **WHEN** an artist is followed whose ID is already among the followed artists
- **THEN** the followed artists SHALL remain unchanged

#### Scenario: Followed artist IDs derivation

- **WHEN** the set of followed artist IDs is accessed
- **THEN** it SHALL return the set of IDs derived from the current followed artists
