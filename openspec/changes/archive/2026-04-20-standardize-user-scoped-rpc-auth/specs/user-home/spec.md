## MODIFIED Requirements

### Requirement: Update Home RPC

The system SHALL provide a dedicated RPC for users to set or change their home area. The request SHALL carry an explicit `user_id` that the backend verifies against the JWT-derived userID; mismatches SHALL be rejected with `PERMISSION_DENIED`.

#### Scenario: Set home area

- **WHEN** an authenticated user calls `UserService.UpdateHome` with a valid structured `Home`
- **AND** the supplied `user_id` equals the userID derived from the JWT
- **THEN** the system SHALL create or update the home record in the `homes` table
- **AND** associate it with the user's `home_id`
- **AND** the response SHALL include the updated `User` entity

#### Scenario: Invalid code values

- **WHEN** `UpdateHome` is called with a `country_code` that is not a valid ISO 3166-1 alpha-2 code
- **OR** a `level_1` that does not match a known ISO 3166-2 subdivision code
- **THEN** the system SHALL return `INVALID_ARGUMENT`

#### Scenario: Unauthenticated request

- **WHEN** `UpdateHome` is called without valid authentication
- **THEN** the system SHALL return `UNAUTHENTICATED`

#### Scenario: user_id does not match authenticated user

- **WHEN** `UpdateHome` is called with a `user_id` that differs from the userID derived from the JWT
- **THEN** the system SHALL return `PERMISSION_DENIED`
- **AND** the `homes` table SHALL NOT be modified

#### Scenario: Missing user_id

- **WHEN** `UpdateHome` is called without a `user_id` field
- **THEN** the system SHALL return `INVALID_ARGUMENT` via `protovalidate` enforcement

### Requirement: Home included in User retrieval

The `User.home` field SHALL be populated in all RPCs that return a `User` entity. `UserService.Get` requests SHALL carry an explicit `user_id` that the backend verifies against the JWT-derived userID; mismatches SHALL be rejected with `PERMISSION_DENIED`.

#### Scenario: Get returns home

- **WHEN** `UserService.Get` is called for a user who has set their home area
- **AND** the supplied `user_id` equals the userID derived from the JWT
- **THEN** the returned `User.home` field SHALL contain the full structured home (country_code, level_1, and level_2 if set)

#### Scenario: Get returns nil home

- **WHEN** `UserService.Get` is called for a user who has not set their home area
- **AND** the supplied `user_id` equals the userID derived from the JWT
- **THEN** the returned `User.home` field SHALL be absent (not set)

#### Scenario: Get rejects mismatched user_id

- **WHEN** `UserService.Get` is called with a `user_id` that differs from the userID derived from the JWT
- **THEN** the system SHALL return `PERMISSION_DENIED`
- **AND** the response SHALL NOT carry any user data
