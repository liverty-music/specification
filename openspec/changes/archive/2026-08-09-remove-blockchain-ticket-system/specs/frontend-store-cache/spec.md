## MODIFIED Requirements

### Requirement: Caching scope is limited to audited read resources
The primitive SHALL be applied only to read-only resources whose value derives from cross-route re-entry: `Concert.listByFollower`, `Concert.listWithProximity`, and `Artist.listTop`. Resources that are requested at most once per session, are network-first for freshness, or are client-owned local state SHALL NOT be cached by the primitive. `User.get` SHALL remain out of scope: it keeps its existing idempotent get-or-create recovery (in-memory + localStorage) and SHALL NOT be migrated onto the primitive. (`Ticket.listTickets` and `Entry.getMerklePath` are removed together with the blockchain ticket system under the Scenario A pivot and are therefore no longer in scope.)

#### Scenario: One-shot per-artist reads are not cached
- **WHEN** `Concert.listConcerts(artistId)` or `Artist.listSimilar(artistId)` is requested
- **THEN** it SHALL be issued as a direct pass-through
- **AND** it SHALL NOT be stored in the primitive

#### Scenario: Network-first resources are not cached
- **WHEN** a network-first resource (`Push.*`, `Artist.search`) is requested
- **THEN** it SHALL be issued fresh
- **AND** it SHALL NOT be served from the primitive

#### Scenario: User.get is not migrated onto the primitive
- **WHEN** the current user entity is read via `User.get`
- **THEN** it SHALL be served by its existing idempotent get-or-create recovery (in-memory + localStorage)
- **AND** it SHALL NOT be routed through the shared primitive
