## ADDED Requirements

### Requirement: User Home Area Data Model

The system SHALL support a `home` field on the User entity representing the user's home area — the geographic area where the user regularly attends live events without considering it a "trip" (遠征). The value is an ISO 3166-2 subdivision code (e.g., `JP-13` for Tokyo).

#### Scenario: Home field in Proto definition

- **WHEN** the `User` proto message is defined
- **THEN** it SHALL include a `Home home` field as an optional value-object message
- **AND** the `Home` message SHALL contain a `string value` field validated to be 2–6 characters (ISO 3166-2 format: `XX-XX` or `XX-XXX`)

#### Scenario: Home field in database

- **WHEN** the `users` table is defined
- **THEN** it SHALL include a nullable `home TEXT` column
- **AND** the column SHALL store an ISO 3166-2 subdivision code

#### Scenario: Home field in Go entity

- **WHEN** the Go `entity.User` struct is defined
- **THEN** it SHALL include a `Home *string` field
- **AND** the value SHALL be an ISO 3166-2 code or nil when not set

### Requirement: Update Home RPC

The system SHALL provide a dedicated RPC for users to set or change their home area.

#### Scenario: Set home area

- **WHEN** an authenticated user calls `UserService.UpdateHome` with a valid ISO 3166-2 code
- **THEN** the system SHALL update the user's `home` field in the database
- **AND** the response SHALL include the updated `User` entity

#### Scenario: Invalid ISO 3166-2 code

- **WHEN** `UpdateHome` is called with a value that does not match a known ISO 3166-2 subdivision code
- **THEN** the system SHALL return `INVALID_ARGUMENT`

#### Scenario: Unauthenticated request

- **WHEN** `UpdateHome` is called without valid authentication
- **THEN** the system SHALL return `UNAUTHENTICATED`

### Requirement: Home included in User retrieval

The `User.home` field SHALL be populated in all RPCs that return a `User` entity.

#### Scenario: Get returns home

- **WHEN** `UserService.Get` is called for a user who has set their home area
- **THEN** the returned `User.home` field SHALL contain the user's ISO 3166-2 code

#### Scenario: Get returns nil home

- **WHEN** `UserService.Get` is called for a user who has not set their home area
- **THEN** the returned `User.home` field SHALL be absent (not set)

### Requirement: Frontend home area persistence via RPC

The frontend SHALL store the user's home area server-side via the `UpdateHome` RPC, replacing localStorage-based persistence for authenticated users.

#### Scenario: Onboarding area selection triggers RPC

- **WHEN** an authenticated user selects their area in the region setup sheet
- **THEN** the frontend SHALL call `UserService.UpdateHome` with the selected ISO 3166-2 code
- **AND** SHALL NOT write to localStorage for the home area

#### Scenario: Dashboard reads home from User entity

- **WHEN** the dashboard loads for an authenticated user
- **THEN** the lane assignment logic SHALL read the user's home area from the `User` entity obtained via `UserService.Get`
- **AND** SHALL NOT read from localStorage

#### Scenario: Guest fallback to localStorage

- **WHEN** a guest (unauthenticated) user selects their area
- **THEN** the frontend SHALL store the selection in localStorage under `guest.home`
- **AND** the dashboard SHALL read from localStorage for lane assignment
