## ADDED Requirements

### Requirement: Per-Entity Store Ownership

Client-side state SHALL be owned by observable **stores** organized by
entity/aggregate, not by authentication state. Each store SHALL own the
observable state for its entity, SHALL internally resolve its source
(guest localStorage vs authenticated backend), and MAY cache read-only
resources. Callers SHALL read state from the store and SHALL NOT branch on
`auth.isAuthenticated` to select a guest-vs-authed source.

#### Scenario: Caller reads without auth branching
- **WHEN** a view model or service needs an entity value owned by a store
- **THEN** it SHALL read the store's exposed observable
- **AND** it SHALL NOT inspect `auth.isAuthenticated` to choose between a guest
  store and an authenticated entity

#### Scenario: UserStore owns home and language for both auth states
- **WHEN** the current user's home area or preferred language is read
- **THEN** it SHALL be sourced from `UserStore`
- **AND** for an authenticated user `UserStore` SHALL surface the backend `User`
  entity values
- **AND** for a guest `UserStore` SHALL surface a synthesized current-user view
  sourced from guest localStorage
- **AND** the exposed value SHALL be observable so dependent bindings
  re-evaluate on change

#### Scenario: Cache-only stores own no guest/authed duality
- **WHEN** a store owns read-only resources (e.g. a top-artists list)
- **THEN** it SHALL cache those resources
- **AND** it SHALL NOT participate in guest→authed transition or sign-out clear

### Requirement: Event-Driven Auth-Boundary Transitions

Guest→authenticated transition and sign-out SHALL be handled per-store via
domain events, with no central orchestrator and no cross-store completion
barrier. Each store SHALL clear its own guest data when its own migration
completes.

#### Scenario: Home and language migrate as Create-time inputs
- **WHEN** a guest signs up
- **THEN** the sign-up flow SHALL read home and language from `UserStore`'s
  guest view and pass them to the user-create call as inputs
- **AND** `UserStore` SHALL persist them, switch its current user to the
  authenticated entity, and clear its own guest localStorage for those fields
- **AND** no post-creation event SHALL be required to migrate home or language

#### Scenario: Follows migrate after the user exists
- **WHEN** the authenticated user has been created
- **THEN** a `UserCreated` event SHALL be published
- **AND** the follow store SHALL migrate guest follows and hype to the backend
  using idempotent calls now that a user id exists
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
