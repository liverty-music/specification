# User

## Purpose

Defines the User entity: its identity, home area and preferred language fields, validation rules, and the conventions authenticated per-user operations follow to scope access to the correct user and report a missing user.

## Requirements

### Requirement: Country Code Extraction

The system SHALL provide a function that extracts the ISO 3166-1 alpha-2 country code from an ISO 3166-2 subdivision code.

#### Scenario: Extract country code from subdivision

- **WHEN** the function receives a valid ISO 3166-2 code (e.g., `JP-13`, `US-NY`)
- **THEN** it SHALL return the two-letter country prefix (e.g., `JP`, `US`)

#### Scenario: Construct structured Home from normalization result

- **WHEN** a free-text admin_area is successfully normalized to an ISO 3166-2 code
- **THEN** the system SHALL be able to derive a `Home` structure with:
  - `country_code` extracted from the ISO 3166-2 prefix
  - `level_1` set to the full ISO 3166-2 code
  - `level_2` absent (normalization only resolves to level_1 in Phase 1)

### Requirement: User ID Propagation

The system SHALL extract the user ID from validated tokens and propagate it through the request context.

**Rationale**: Handlers need access to the authenticated user ID to scope operations correctly (e.g., following artists, viewing followed content). The `external_id` (Zitadel `sub`) enables identity resolution against the local database.

#### Scenario: Authenticated Request

- **WHEN** a JWT token is successfully validated
- **THEN** the system extracts the user ID from the token's `sub` claim
- **AND** adds the user ID to the request context as `external_id`
- **AND** makes the user ID accessible to downstream handlers

### Requirement: Home validation

The `Home` entity SHALL provide a `Validate() error` method that enforces structural integrity of geographic home area data. The method SHALL return the first validation error encountered.

Validation rules:
1. `CountryCode` MUST match ISO 3166-1 alpha-2 format (`^[A-Z]{2}$`).
2. `Level1` MUST match ISO 3166-2 subdivision format (`^[A-Z]{2}-[A-Z0-9]{1,3}$`).
3. The first two characters of `Level1` MUST equal `CountryCode`.
4. When `Level2` is non-nil, its length MUST be between 1 and 20 characters inclusive.

#### Scenario: Valid home with all fields

- **WHEN** Home has CountryCode="JP", Level1="JP-13", Level2=nil
- **THEN** Validate returns nil

#### Scenario: Valid home with Level2

- **WHEN** Home has CountryCode="JP", Level1="JP-13", Level2="Shibuya"
- **THEN** Validate returns nil

#### Scenario: Invalid country code format

- **WHEN** Home has CountryCode="j" (lowercase or wrong length)
- **THEN** Validate returns error mentioning "ISO 3166-1 alpha-2"

#### Scenario: Invalid Level1 format

- **WHEN** Home has Level1="INVALID"
- **THEN** Validate returns error mentioning "ISO 3166-2"

#### Scenario: Level1 prefix mismatch

- **WHEN** Home has CountryCode="JP" but Level1="US-CA"
- **THEN** Validate returns error mentioning prefix mismatch

#### Scenario: Level2 empty string

- **WHEN** Home has Level2 pointing to an empty string
- **THEN** Validate returns error mentioning "1 and 20 characters"

#### Scenario: Level2 too long

- **WHEN** Home has Level2 pointing to a 21-character string
- **THEN** Validate returns error mentioning "1 and 20 characters"

---

### Requirement: Handlers return NotFound when user record does not exist
If `GetByExternalID` returns no user (e.g., user has a valid JWT but no record in `users`), the resolution layer SHALL return `CodeNotFound`.

#### Scenario: Valid JWT but no user record
- **WHEN** an authenticated request arrives but `GetByExternalID` finds no matching user
- **THEN** the handler or use case returns `connect.CodeNotFound` with message "user not found"

### Requirement: Explicit user_id scoping for authenticated per-user RPCs

The system SHALL require that every authenticated RPC scoped to a specific user — except creation RPCs where the caller's internal user ID does not yet exist — carries an explicit `entity.v1.UserId` field in its request message. The field SHALL be marked required via `protovalidate`. The backend SHALL compare the supplied value against the userID derived from the JWT context and reject mismatches with `PERMISSION_DENIED`. Creation RPCs that mint a new internal user record are exempt from this `user_id` convention: such RPCs SHALL identify the caller via `external_id` (the identity provider's `sub` claim) extracted from the JWT, not via a client-supplied `user_id`.

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

#### Scenario: User creation does not require user_id

- **WHEN** a client calls `UserService.Create` (or any analogous creation RPC that mints a new internal user ID)
- **THEN** the request SHALL NOT carry a `user_id` field
- **AND** the backend SHALL extract `external_id` from the JWT context to identify the identity provider user
- **AND** the backend SHALL return the newly minted `UserId` in the response for the client to use on subsequent RPCs

### Requirement: User Home Area Data Model

The system SHALL support a structured `home` field on the User entity representing the user's home area — the geographic area where the user regularly attends live events without considering it a "trip" (遠征). The value is a structured geographic location expressed through a hierarchy of internationally standardized codes, with centroid coordinates for proximity calculations.

#### Scenario: Home message in Proto definition

- **WHEN** the `Home` proto message is defined
- **THEN** it SHALL contain a `string country_code` field validated as ISO 3166-1 alpha-2 (exactly two uppercase Latin letters, e.g., `JP`, `US`)
- **AND** a `string level_1` field validated as ISO 3166-2 format (4–6 characters, e.g., `JP-13`, `US-NY`)
- **AND** an `optional string level_2` field for finer-grained subdivision (1–20 characters when present)
- **AND** an `optional double centroid_latitude` field for the centroid latitude
- **AND** an `optional double centroid_longitude` field for the centroid longitude

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
- **AND** a nullable `centroid_latitude DOUBLE PRECISION` column for the centroid latitude
- **AND** a nullable `centroid_longitude DOUBLE PRECISION` column for the centroid longitude

#### Scenario: Home field in Go entity

- **WHEN** the Go `entity.Home` struct is defined
- **THEN** it SHALL include `ID string`, `CountryCode string`, `Level1 string`, `Level2 *string`, and `Centroid *Coordinates` fields
- **AND** the `entity.User` struct SHALL include a `Home *Home` field
- **AND** a nil `Home` SHALL mean the user has not set their home area

#### Scenario: Centroid populated at write time

- **WHEN** `UserRepository.Create` or `UserRepository.UpdateHome` is called with a `Home` value
- **THEN** the repository implementation SHALL resolve the `Level1` ISO 3166-2 code to centroid coordinates
- **AND** store the resolved `centroid_latitude` and `centroid_longitude` alongside the other home fields
- **AND** the centroid resolution logic SHALL be an infrastructure implementation detail (not visible to usecase/entity layers)

#### Scenario: Code system contract for level_2

- **WHEN** `level_2` is populated
- **THEN** its code system SHALL be determined by `country_code`:
  - `JP` → future use (not yet defined; Phase 1 always omits level_2)
  - `US` → FIPS county code (e.g., `06037` for Los Angeles County)
  - `DE` → AGS code (e.g., `09162` for Munich)
- **AND** additional country mappings SHALL be documented in the `Home` proto message comment as they are introduced

### Requirement: User Preferred Language Field on User Entity

The `entity.v1.User` message SHALL expose the user's preferred display language as an ISO 639-1 two-letter code, distinguishable from the unset state.

#### Scenario: Preferred language present

- **WHEN** the backend returns a `User` entity for a row whose `preferred_language` column is non-NULL
- **THEN** the proto response SHALL include `preferred_language` set to the stored ISO 639-1 code (e.g., `"ja"` or `"en"`)
- **AND** the code SHALL match `^[a-z]{2}$`

#### Scenario: Preferred language unset (legacy or new row before backfill)

- **WHEN** the backend returns a `User` entity for a row whose `preferred_language` column is NULL
- **THEN** the proto response SHALL signal absence via the `optional` field marker (the field SHALL NOT be present in the wire response)
- **AND** clients SHALL interpret absence as "client must backfill on next observation"
