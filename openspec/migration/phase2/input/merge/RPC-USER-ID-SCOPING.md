<!-- merge_group: RPC-USER-ID-SCOPING | target: components/entity/user | members: 2 -->

<!-- member: rpc-auth-scoping | flags:  -->
### Requirement: Explicit user_id in authenticated per-user RPC bodies

The system SHALL require that every authenticated RPC scoped to a specific user — except creation RPCs where the caller's internal user ID does not yet exist — carries an explicit `entity.v1.UserId` field in its request message. The field SHALL be marked required via `protovalidate`. The backend SHALL compare the supplied value against the userID derived from the JWT context and reject mismatches with `PERMISSION_DENIED`.

#### Scenario: Matching user_id passes authorization

- **WHEN** an authenticated client calls a per-user RPC with `user_id` equal to the JWT-derived userID
- **THEN** the handler SHALL proceed with normal processing

#### Scenario: Mismatched user_id is rejected

- **WHEN** an authenticated client calls a per-user RPC with `user_id` that differs from the JWT-derived userID
- **THEN** the handler SHALL return `PERMISSION_DENIED`
- **AND** no business logic SHALL execute
- **AND** the response SHALL NOT reveal whether the requested user exists or what data they have

#### Scenario: Missing user_id is rejected

- **WHEN** an authenticated client calls a per-user RPC with an absent or empty `user_id`
- **THEN** the handler SHALL return `INVALID_ARGUMENT` via `protovalidate` enforcement

#### Scenario: Unauthenticated request is rejected before user_id check

- **WHEN** a client calls a per-user RPC without a valid JWT
- **THEN** the authentication middleware SHALL reject the request with `UNAUTHENTICATED` before the `user_id` check runs

<!-- member: rpc-auth-scoping | flags:  -->
### Requirement: Creation RPCs are exempt from the user_id convention

The system SHALL treat creation RPCs that mint a new internal user record as an exception to the `user_id` convention. Such RPCs SHALL identify the caller via `external_id` (the identity provider's `sub` claim) extracted from the JWT, not via a client-supplied `user_id`.

#### Scenario: User creation does not require user_id

- **WHEN** a client calls `UserService.Create` (or any analogous creation RPC that mints a new internal user ID)
- **THEN** the request SHALL NOT carry a `user_id` field
- **AND** the backend SHALL extract `external_id` from the JWT context to identify the identity provider user
- **AND** the backend SHALL return the newly minted `UserId` in the response for the client to use on subsequent RPCs

