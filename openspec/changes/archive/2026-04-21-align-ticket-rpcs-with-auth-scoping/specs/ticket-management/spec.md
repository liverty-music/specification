## ADDED Requirements

### Requirement: MintTicket request carries explicit user_id

The `TicketService.MintTicket` RPC SHALL carry an explicit `entity.v1.UserId user_id` field in its request message. The field SHALL be marked required via `protovalidate`. The backend SHALL compare the supplied value against the userID derived from the JWT context and reject mismatches with `PERMISSION_DENIED` via the shared `requireMatchingUserID` helper defined by the `rpc-auth-scoping` capability.

#### Scenario: Matching user_id mints ticket

- **WHEN** an authenticated fan calls `MintTicket` with `user_id` equal to the JWT-derived userID for a valid `event_id`
- **THEN** the handler SHALL proceed to resolve the caller's Safe address and submit the mint transaction
- **AND** the response SHALL contain the newly minted `Ticket`

#### Scenario: Mismatched user_id is rejected

- **WHEN** an authenticated fan calls `MintTicket` with `user_id` that differs from the JWT-derived userID
- **THEN** the handler SHALL return `PERMISSION_DENIED`
- **AND** no on-chain transaction SHALL be submitted
- **AND** no row SHALL be inserted into the `tickets` table
- **AND** the response SHALL NOT reveal whether the requested user exists or holds tickets

#### Scenario: Missing user_id is rejected

- **WHEN** an authenticated fan calls `MintTicket` with an absent or empty `user_id`
- **THEN** the handler SHALL return `INVALID_ARGUMENT` via `protovalidate` enforcement
- **AND** the rejection SHALL occur before any business logic executes

#### Scenario: Unauthenticated request is rejected before user_id check

- **WHEN** a client calls `MintTicket` without a valid JWT
- **THEN** the authentication middleware SHALL reject the request with `UNAUTHENTICATED` before the `user_id` check runs

---

### Requirement: ListTickets request carries explicit user_id

The `TicketService.ListTickets` RPC SHALL carry an explicit `entity.v1.UserId user_id` field in its request message. The field SHALL be marked required via `protovalidate`. The backend SHALL compare the supplied value against the userID derived from the JWT context and reject mismatches with `PERMISSION_DENIED` via the shared `requireMatchingUserID` helper.

#### Scenario: Matching user_id returns the caller's tickets

- **WHEN** an authenticated fan calls `ListTickets` with `user_id` equal to the JWT-derived userID
- **THEN** the handler SHALL return every `Ticket` currently held by that user
- **AND** no tickets belonging to other users SHALL appear in the response

#### Scenario: Mismatched user_id is rejected

- **WHEN** an authenticated fan calls `ListTickets` with `user_id` that differs from the JWT-derived userID
- **THEN** the handler SHALL return `PERMISSION_DENIED`
- **AND** the response SHALL NOT reveal whether the requested user exists or holds tickets

#### Scenario: Missing user_id is rejected

- **WHEN** an authenticated fan calls `ListTickets` with an absent or empty `user_id`
- **THEN** the handler SHALL return `INVALID_ARGUMENT` via `protovalidate` enforcement

---

### Requirement: GetTicket remains identifier-scoped

The `TicketService.GetTicket` RPC SHALL remain keyed by `ticket_id` and SHALL NOT carry a `user_id` field. The ticket identifier itself provides the authorization scope for this RPC; the `rpc-auth-scoping` convention does not apply.

#### Scenario: GetTicket request shape

- **WHEN** a client calls `GetTicket`
- **THEN** the request SHALL contain only `ticket_id` as its identifying field
- **AND** the handler SHALL return the ticket matching that identifier
- **AND** the handler SHALL NOT perform a JWT-userID vs request-userID comparison
