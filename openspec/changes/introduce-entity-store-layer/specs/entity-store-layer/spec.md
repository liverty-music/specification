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

### Requirement: Boot Reconciliation of Unmerged Guest Data

Each store SHALL reconcile leftover guest data at application start to heal
partial-migration failures, without in-flight retry coordination. The
reconciliation SHALL be idempotent and SHALL NOT resurrect state the user has
already changed after signup.

#### Scenario: Leftover guest data reconciled on authenticated boot
- **WHEN** the application starts
- **AND** the user is authenticated
- **AND** a store finds leftover guest data in localStorage that should have
  migrated
- **THEN** the store SHALL re-run its idempotent migration and then clear the
  leftover guest data

#### Scenario: Reconciliation does not resurrect reverted state
- **WHEN** boot reconciliation runs
- **THEN** it SHALL run in the earliest boot phase, before the UI is interactive
- **AND** it SHALL be guarded so it runs at most once per session
- **AND** guest localStorage SHALL be treated as a pending-migration queue that
  is drained promptly on a successful migrate, minimizing the
  migrated-but-not-cleared window
