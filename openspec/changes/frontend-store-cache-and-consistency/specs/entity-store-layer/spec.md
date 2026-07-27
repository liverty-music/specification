## MODIFIED Requirements

### Requirement: Per-Entity Store Ownership

Client-side state SHALL be owned by observable **stores** organized by
entity/aggregate, not by authentication state. Each store SHALL own the
observable state for its entity, SHALL internally resolve its source
(guest localStorage vs authenticated backend), and SHALL obtain any read-only
resource caching from the shared `frontend-store-cache` primitive rather than a
bespoke per-store TTL, in-flight coalescing, or invalidation implementation. The
store SHALL remain the single source of truth for its resource; the primitive is
an internal collaborator, and callers SHALL read state only from the store's
exposed observable. Callers SHALL read state from the store and SHALL NOT branch
on `auth.isAuthenticated` to select a guest-vs-authed source.

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

#### Scenario: Caching goes through the shared primitive
- **WHEN** a store needs to cache a read-only resource
- **THEN** it SHALL use the shared `frontend-store-cache` primitive for storage,
  staleness, in-flight coalescing, and invalidation
- **AND** it SHALL NOT hand-roll a separate TTL cache
- **AND** exactly one copy of the resource SHALL exist, owned by the store, with
  consumers reading it only through the store's observable state

## ADDED Requirements

### Requirement: Ticket-journey status is a single source of truth
Ticket-journey status SHALL be owned by a single observable store (a `TicketJourneyStore`) exposing an observable map of event id to journey status. Reads (`listByUser`) SHALL populate the store and SHALL be treated as always-fresh (network-first, no stale window). Writes (`SetStatus`, `Delete`) SHALL be write-through: they SHALL issue the RPC and then update the store's observable map. All consumers — the Dashboard and the event detail sheet — SHALL read journey status from this store, so a status change from any surface is reflected everywhere without a re-fetch or route re-entry. The store SHALL clear its journey state on sign-out.

#### Scenario: Sheet write reflects on the Dashboard without re-entry
- **WHEN** the user changes a journey status in the event detail sheet
- **THEN** the store's observable journey map SHALL be updated after the write RPC succeeds
- **AND** the Dashboard's rendering of that event's status SHALL update without re-fetching or re-entering the route

#### Scenario: Single shared journey state
- **WHEN** both the Dashboard and the detail sheet render a journey status for the same event
- **THEN** both SHALL read from the same `TicketJourneyStore` observable map
- **AND** they SHALL NOT hold separate copies of the status

#### Scenario: Journey read is always fresh
- **WHEN** the Dashboard loads and requests journey status via the store
- **THEN** the store SHALL fetch `listByUser` fresh (no stale window)
- **AND** it SHALL surface the result via its observable map

#### Scenario: Write failure does not desync the store
- **WHEN** a journey `SetStatus`/`Delete` RPC fails
- **THEN** the store's observable map SHALL NOT be updated to the attempted value

#### Scenario: Journey state cleared on sign-out
- **WHEN** the user signs out
- **THEN** the `TicketJourneyStore` SHALL clear its journey map
- **AND** no prior user's journey status SHALL be readable afterward
