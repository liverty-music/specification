<!-- spec: entity-store-layer | target: components/usecase/ticket-journey/set-status | flags: CLASSNAME | new_name: Ticket-journey status is a single source of truth -->

### Requirement: Ticket-journey status is a single source of truth
Ticket-journey status SHALL be owned by a single observable store exposing an observable map of event id to journey status. Reads (`listByUser`) SHALL populate the store and SHALL be treated as always-fresh (network-first, no stale window). Writes (`SetStatus`, `Delete`) SHALL be write-through: they SHALL issue the RPC and then update the store's observable map. All consumers — the Dashboard and the event detail sheet — SHALL read journey status from this store, so a status change from any surface is reflected everywhere without a re-fetch or route re-entry. The store SHALL clear its journey state on sign-out.

#### Scenario: Sheet write reflects on the Dashboard without re-entry
- **WHEN** the user changes a journey status in the event detail sheet
- **THEN** the store's observable journey map SHALL be updated after the write RPC succeeds
- **AND** the Dashboard's rendering of that event's status SHALL update without re-fetching or re-entering the route

#### Scenario: Single shared journey state
- **WHEN** both the Dashboard and the detail sheet render a journey status for the same event
- **THEN** both SHALL read from the same observable map
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
- **THEN** the store SHALL clear its journey map
- **AND** no prior user's journey status SHALL be readable afterward
