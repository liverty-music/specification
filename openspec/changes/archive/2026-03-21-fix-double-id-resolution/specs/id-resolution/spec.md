## MODIFIED Requirements

### Requirement: RPC handlers resolve Zitadel external ID to internal UUID before database access
All authenticated RPC handlers that write or query per-user rows in the database SHALL ensure that the JWT `sub` claim (Zitadel external ID) is resolved to the internal `users.id` UUID before any database access. The resolution SHALL occur at exactly one layer — either in the handler or in the use case — never both. Passing the raw JWT `sub` claim to a UUID column is prohibited.

When the use case owns ID resolution internally (e.g., via a `resolveUserID` helper), the handler SHALL pass `claims.Sub` directly to the use case. When the use case accepts an internal UUID directly, the handler SHALL resolve `claims.Sub` to `users.id` before calling the use case.

#### Scenario: Authenticated user calls FollowService/Follow
- **WHEN** an authenticated user calls `FollowService/Follow`
- **THEN** the handler passes `claims.Sub` to the use case, which resolves it to `users.id` internally and uses `users.id` for the `followed_artists.user_id` column

#### Scenario: Authenticated user calls FollowService/Unfollow
- **WHEN** an authenticated user calls `FollowService/Unfollow`
- **THEN** the handler passes `claims.Sub` to the use case, which resolves it to `users.id` internally and uses `users.id` for the delete operation

#### Scenario: Authenticated user calls FollowService/ListFollowed
- **WHEN** an authenticated user calls `FollowService/ListFollowed`
- **THEN** the handler passes `claims.Sub` to the use case, which resolves it to `users.id` and queries `followed_artists` with the internal UUID

#### Scenario: Authenticated user calls FollowService/SetHype
- **WHEN** an authenticated user calls `FollowService/SetHype`
- **THEN** the handler passes `claims.Sub` to the use case, which resolves it to `users.id` and updates `followed_artists` with the internal UUID

#### Scenario: Authenticated user calls TicketJourneyService/SetStatus
- **WHEN** an authenticated user calls `TicketJourneyService/SetStatus`
- **THEN** the handler resolves `claims.Sub` to `users.id` via `GetByExternalID` and writes to `ticket_journeys` with the internal UUID

#### Scenario: Authenticated user calls TicketJourneyService/Delete
- **WHEN** an authenticated user calls `TicketJourneyService/Delete`
- **THEN** the handler resolves `claims.Sub` to `users.id` via `GetByExternalID` and deletes from `ticket_journeys` using the internal UUID

#### Scenario: Authenticated user calls TicketJourneyService/ListByUser
- **WHEN** an authenticated user calls `TicketJourneyService/ListByUser`
- **THEN** the handler resolves `claims.Sub` to `users.id` via `GetByExternalID` and queries `ticket_journeys` with the internal UUID

#### Scenario: Authenticated user calls TicketEmailService/CreateTicketEmail
- **WHEN** an authenticated user calls `TicketEmailService/CreateTicketEmail`
- **THEN** the handler resolves `claims.Sub` to `users.id` via `GetByExternalID` and writes to `ticket_emails` with the internal UUID

#### Scenario: Authenticated user calls TicketEmailService/UpdateTicketEmail
- **WHEN** an authenticated user calls `TicketEmailService/UpdateTicketEmail`
- **THEN** the handler resolves `claims.Sub` to `users.id` via `GetByExternalID` and authorizes the update using the internal UUID

#### Scenario: ID resolution occurs exactly once per request
- **WHEN** any authenticated RPC is processed
- **THEN** `GetByExternalID` is called exactly once — either in the handler or in the use case, not in both

### Requirement: Handlers return NotFound when user record does not exist
If `GetByExternalID` returns no user (e.g., user has a valid JWT but no record in `users`), the resolution layer SHALL return `CodeNotFound`.

#### Scenario: Valid JWT but no user record
- **WHEN** an authenticated request arrives but `GetByExternalID` finds no matching user
- **THEN** the handler or use case returns `connect.CodeNotFound` with message "user not found"
