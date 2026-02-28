## ADDED Requirements

### Requirement: User Home Area Data Model

The system SHALL support a structured `home` field on the User entity representing the user's home area — the geographic area where the user regularly attends live events without considering it a "trip" (遠征). The value is a structured geographic location expressed through a hierarchy of internationally standardized codes.

#### Scenario: Home message in Proto definition

- **WHEN** the `Home` proto message is defined
- **THEN** it SHALL contain a `string country_code` field validated as ISO 3166-1 alpha-2 (exactly two uppercase Latin letters, e.g., `JP`, `US`)
- **AND** a `string level_1` field validated as ISO 3166-2 format (4–6 characters, e.g., `JP-13`, `US-NY`)
- **AND** an `optional string level_2` field for finer-grained subdivision (1–20 characters when present)

#### Scenario: Home field on User message

- **WHEN** the `User` proto message is defined
- **THEN** it SHALL include a `Home home` field as an optional structured message
- **AND** the field SHALL be absent until the user explicitly selects their area

#### Scenario: Home field in database

- **WHEN** the `homes` table is defined
- **THEN** it SHALL include a primary key `id TEXT`
- **AND** a required `country_code TEXT` column storing an ISO 3166-1 alpha-2 code
- **AND** a required `level_1 TEXT` column storing an ISO 3166-2 subdivision code
- **AND** a nullable `level_2 TEXT` column storing a country-specific finer area code
- **AND** the `users` table SHALL reference `homes.id` via a nullable `home_id TEXT` foreign key

#### Scenario: Home field in Go entity

- **WHEN** the Go `entity.Home` struct is defined
- **THEN** it SHALL include `ID string`, `CountryCode string`, `Level1 string`, and `Level2 *string` fields
- **AND** the `entity.User` struct SHALL include a `Home *Home` field
- **AND** a nil `Home` SHALL mean the user has not set their home area

#### Scenario: Code system contract for level_2

- **WHEN** `level_2` is populated
- **THEN** its code system SHALL be determined by `country_code`:
  - `JP` → future use (not yet defined; Phase 1 always omits level_2)
  - `US` → FIPS county code (e.g., `06037` for Los Angeles County)
  - `DE` → AGS code (e.g., `09162` for Munich)
- **AND** additional country mappings SHALL be documented in the `Home` proto message comment as they are introduced

### Requirement: Create User with Home

The system SHALL accept an optional home area during user creation, allowing the home selected during onboarding to be persisted atomically with the user record.

#### Scenario: Create user with home provided

- **WHEN** an authenticated user calls `UserService.Create` with a valid `home` field
- **THEN** the system SHALL create the user record and the associated home record in a single transaction
- **AND** the response SHALL include the created `User` entity with the `home` field populated

#### Scenario: Create user without home

- **WHEN** an authenticated user calls `UserService.Create` without a `home` field
- **THEN** the system SHALL create the user record with `home_id = NULL`
- **AND** the response SHALL include the created `User` entity with `home` absent

### Requirement: Update Home RPC

The system SHALL provide a dedicated RPC for users to set or change their home area.

#### Scenario: Set home area

- **WHEN** an authenticated user calls `UserService.UpdateHome` with a valid structured `Home`
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

### Requirement: Home included in User retrieval

The `User.home` field SHALL be populated in all RPCs that return a `User` entity.

#### Scenario: Get returns home

- **WHEN** `UserService.Get` is called for a user who has set their home area
- **THEN** the returned `User.home` field SHALL contain the full structured home (country_code, level_1, and level_2 if set)

#### Scenario: Get returns nil home

- **WHEN** `UserService.Get` is called for a user who has not set their home area
- **THEN** the returned `User.home` field SHALL be absent (not set)

### Requirement: Frontend home area persistence via RPC

The frontend SHALL store the user's home area server-side via RPC, replacing localStorage-based persistence for authenticated users.

#### Scenario: Onboarding area selection persisted at account creation

- **WHEN** a guest user has selected their area during onboarding
- **AND** the user subsequently creates an account
- **THEN** the frontend SHALL include the selected home in the `UserService.Create` request
- **AND** SHALL NOT make a separate `UpdateHome` call for the initial home

#### Scenario: Settings area change triggers UpdateHome RPC

- **WHEN** an authenticated user changes their area in settings
- **THEN** the frontend SHALL call `UserService.UpdateHome` with the new structured home
- **AND** SHALL NOT write to localStorage for the home area

#### Scenario: Dashboard reads home from User entity

- **WHEN** the dashboard loads for an authenticated user
- **THEN** the lane assignment logic SHALL read the user's home area from the `User` entity obtained via `UserService.Get`
- **AND** SHALL NOT read from localStorage

#### Scenario: Guest fallback to localStorage

- **WHEN** a guest (unauthenticated) user selects their area
- **THEN** the frontend SHALL store the selection in localStorage under `guest.home`
- **AND** the dashboard SHALL read from localStorage for lane assignment
