## ADDED Requirements

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

---

### Requirement: Create RPC Captures Preferred Language at Signup

The `UserService.Create` RPC SHALL accept a required `preferred_language` field carrying the client's effective locale at the moment of signup, and SHALL persist it atomically with the new user row.

#### Scenario: Successful Create persists the supplied language

- **WHEN** a client calls `Create` with `preferred_language = "ja"` and an unprovisioned `external_id`
- **THEN** the backend SHALL persist `preferred_language = "ja"` on the new `users` row
- **AND** the returned `User` entity SHALL include `preferred_language = "ja"`

#### Scenario: Create rejects missing or malformed preferred_language

- **WHEN** a client calls `Create` without `preferred_language` or with a value that does not match `^[a-z]{2}$`
- **THEN** the backend SHALL reject the request with `INVALID_ARGUMENT`
- **AND** no user row SHALL be created

#### Scenario: Idempotent Create does NOT overwrite existing language

- **WHEN** `Create` is called with an `external_id` that already exists in the database
- **AND** the request carries `preferred_language = "en"`
- **AND** the existing row has `preferred_language = "ja"`
- **THEN** the backend SHALL return `OK` with the existing user
- **AND** the stored `preferred_language` SHALL remain `"ja"` (the duplicate call is a read, not an upsert — mirroring the existing rule for `home`)

---

### Requirement: UpdatePreferredLanguage RPC

The `UserService.UpdatePreferredLanguage` RPC SHALL allow an authenticated user to change their stored preferred language. The RPC SHALL follow the rpc-auth-scoping convention — the request carries an explicit `user_id` that the backend verifies against the caller's JWT-derived userID.

#### Scenario: Successful language update

- **WHEN** an authenticated user calls `UpdatePreferredLanguage` with their own `user_id` and `preferred_language = "en"`
- **THEN** the backend SHALL persist `preferred_language = "en"` on the user's row
- **AND** the response SHALL return the updated `User` entity with `preferred_language = "en"`

#### Scenario: Cross-user update is rejected

- **WHEN** an authenticated user calls `UpdatePreferredLanguage` with a `user_id` that does not match their JWT-derived userID
- **THEN** the backend SHALL reject the request with `PERMISSION_DENIED`
- **AND** no DB write SHALL occur

#### Scenario: Malformed language code is rejected

- **WHEN** the request carries `preferred_language` not matching `^[a-z]{2}$` (e.g., `""`, `"jpn"`, `"JA"`, `"ja-JP"`)
- **THEN** the backend SHALL reject the request with `INVALID_ARGUMENT`

#### Scenario: Unknown user is rejected

- **WHEN** the request is well-formed but the JWT-derived user has no corresponding `users` row
- **THEN** the backend SHALL reject the request with `NOT_FOUND`

#### Scenario: Unauthenticated request is rejected

- **WHEN** the request lacks valid authentication credentials
- **THEN** the backend SHALL reject the request with `UNAUTHENTICATED`

---

### Requirement: DB Column Semantics — NULL Means "Not Yet Set by Client"

The `app.users.preferred_language` column SHALL NOT carry a server-side `DEFAULT` value. NULL SHALL denote "client has not yet asserted a language preference" and SHALL be the trigger for client-side backfill on next observation.

#### Scenario: New row from Create always has a non-NULL language

- **WHEN** a row is inserted via the Create RPC
- **THEN** `preferred_language` SHALL be non-NULL (the Create contract requires the field)

#### Scenario: Legacy rows are NULL until backfilled

- **WHEN** the migration runs against an existing database
- **THEN** all rows previously holding `'en'` from the dropped DEFAULT SHALL be set to NULL
- **AND** clients observing NULL SHALL call `UpdatePreferredLanguage` with their currently effective locale to backfill

#### Scenario: Column comment documents the semantics

- **WHEN** an operator inspects `\d+ app.users` or queries `pg_description` for the column
- **THEN** the comment SHALL state that NULL means "not yet set by client; client backfills via UpdatePreferredLanguage on first observation"
