<!-- spec: entity-store-layer | target: stories/merge-guest-data-on-signup | flags: CLASSNAME | new_name: Event-Driven Auth-Boundary Transitions -->

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
