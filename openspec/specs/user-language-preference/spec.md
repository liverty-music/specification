# User Language Preference

## Purpose

Persists each authenticated user's display language in the backend database so language is consistent across devices and browser sessions. Defines the proto-surface (entity field, Create capture, UpdatePreferredLanguage RPC), the storage semantics (NULL = "not yet set by client"), and the repository scan contract that prevents NULL-column reads from masquerading as `not_found` / `already_exists` at the wire boundary.
## Requirements
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

### Requirement: Create RPC Captures Preferred Language at Signup

The `UserService.Create` RPC SHALL accept an optional `preferred_language` field carrying the client's effective locale at the moment of signup. When the field is present, the backend SHALL persist it atomically with the new user row; when absent, the row SHALL be created with NULL and the client SHALL backfill on next hydration via `UpdatePreferredLanguage`. The field is `optional` on the wire so the RPC stays backward-compatible during a rolling deploy where the new backend may briefly serve old frontend clients.

#### Scenario: Successful Create persists the supplied language

- **WHEN** a client calls `Create` with `preferred_language = "ja"` and an unprovisioned `external_id`
- **THEN** the backend SHALL persist `preferred_language = "ja"` on the new `users` row
- **AND** the returned `User` entity SHALL include `preferred_language = "ja"`

#### Scenario: Create accepts absent preferred_language for old clients

- **WHEN** a client calls `Create` without supplying the `preferred_language` field at all (i.e. the field is absent on the wire, as an unupdated client would send)
- **THEN** the backend SHALL create the user row with `preferred_language` as NULL
- **AND** the returned `User` entity SHALL NOT include `preferred_language`
- **AND** subsequent hydration SHALL trigger client-side backfill via `UpdatePreferredLanguage`

#### Scenario: Create rejects malformed preferred_language

- **WHEN** a client calls `Create` with `preferred_language` explicitly present but not matching `^[a-z]{2}$` (e.g., `""`, `"jpn"`, `"JA"`, `"ja-JP"`)
- **THEN** the backend SHALL reject the request with `INVALID_ARGUMENT`
- **AND** no user row SHALL be created

#### Scenario: Idempotent Create does NOT overwrite existing language

- **WHEN** `Create` is called with an `external_id` that already exists in the database
- **AND** the request carries `preferred_language = "en"`
- **AND** the existing row has `preferred_language = "ja"`
- **THEN** the backend SHALL return `OK` with the existing user
- **AND** the stored `preferred_language` SHALL remain `"ja"` (the duplicate call is a read, not an upsert — mirroring the existing rule for `home`)

#### Scenario: Create retry surfaces non-NotFound errors truthfully

- **WHEN** `Create`'s INSERT fails with `unique_violation`
- **AND** the idempotent retry `GetByExternalID(claims.sub)` returns an error
- **AND** that error's code is NOT `NotFound` (e.g., `Internal` from a scan failure or `Unavailable` from a transient pool error)
- **THEN** the backend SHALL respond with the retry's error code, not the original `AlreadyExists`
- **AND** the backend SHALL log a WARN with both errors so the operator sees the full context

#### Scenario: Create retry treats NotFound as the email-collision case

- **WHEN** `Create`'s INSERT fails with `unique_violation`
- **AND** the idempotent retry `GetByExternalID(claims.sub)` returns `NotFound`
- **THEN** the backend SHALL respond with the original `AlreadyExists`

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

### Requirement: DB Column Semantics — NULL Means "Not Yet Set by Client"

The `app.users.preferred_language` column SHALL NOT carry a server-side `DEFAULT` value. NULL SHALL denote "client has not yet asserted a language preference" and SHALL be the trigger for client-side backfill on next observation.

#### Scenario: New row from Create carries the client-supplied language

- **WHEN** a row is inserted via the Create RPC with `preferred_language` present
- **THEN** `preferred_language` SHALL hold that value

#### Scenario: New row from Create without language is NULL

- **WHEN** a row is inserted via the Create RPC without `preferred_language`
- **THEN** `preferred_language` SHALL be NULL
- **AND** the next hydration SHALL backfill it via `UpdatePreferredLanguage`

#### Scenario: Legacy rows are NULL until backfilled

- **WHEN** the migration runs against an existing database
- **THEN** every row with a non-NULL `preferred_language` SHALL be set to NULL — including rows that had been explicitly set by users before this change shipped, not only rows holding the dropped `'en'` DEFAULT (the shipped migration is `UPDATE app.users SET preferred_language = NULL WHERE preferred_language IS NOT NULL`)
- **AND** clients observing NULL SHALL call `UpdatePreferredLanguage` with their currently effective locale to backfill — for rows whose pre-migration value differed from the device's current locale, this results in the user-visible language matching the device, which is the intended "client owns the preference" semantics

#### Scenario: Column comment documents the semantics

- **WHEN** an operator inspects `\d+ app.users` or queries `pg_description` for the column
- **THEN** the comment SHALL state that NULL means "not yet set by client; client backfills via UpdatePreferredLanguage on first observation"

### Requirement: Repository NULL-Safe Reads on Nullable users Columns

Every nullable column on the `users` table (currently `preferred_language`, `country`, `time_zone`, `safe_address`) SHALL be read in a NULL-safe way so that a NULL value never propagates as a pgx scan error. Two equivalent patterns are accepted:

1. **Go-side `sql.NullString` intermediate** — the SELECT scans into a `sql.NullString` local, and the entity field is assigned from the intermediate's `.String` only when `.Valid`; otherwise the field is left at its zero value (empty string). This is the pattern used for `preferred_language`, `country`, and `time_zone`.
2. **SQL-side `COALESCE(col, '')`** — the SELECT projects the column through `COALESCE(col, '')` so pgx never sees a NULL at the scan boundary. This is the pattern used for `safe_address` (since the very first commit that introduced the column).

Both patterns SHALL apply uniformly across `Get`, `GetByExternalID`, `GetByEmail`, `Update`, `UpdateHome` (post-update re-scan), and `List` since they share the same scanner.

Rationale: pgx returns an error when scanning SQL NULL into a non-nullable Go `string`. The next migration or operator-side write that introduces a NULL into a column read with neither pattern in place would cause every read of that row to fail at the wire boundary, manifesting at the handler layer as `not_found` / `already_exists` and masking the true cause.

#### Scenario: Scan succeeds when a nullable column is NULL

- **WHEN** `scanUser` reads a row whose `preferred_language` (or `country`, or `time_zone`, or `safe_address`) is NULL
- **THEN** the scan SHALL succeed without error
- **AND** the corresponding entity field SHALL be the zero value (empty string)
- **AND** higher layers SHALL interpret the zero value as "absent" per the entity convention

#### Scenario: Scan preserves the value when the nullable column has a value

- **WHEN** `scanUser` reads a row whose `preferred_language` is the string `"ja"`
- **THEN** the entity's `PreferredLanguage` field SHALL be the string `"ja"`
- **AND** the same SHALL hold for `country`, `time_zone`, and `safe_address` when populated

#### Scenario: Write boundary helper round-trips empty string as SQL NULL

- **WHEN** a repository write method receives an entity whose `PreferredLanguage` field is the empty string
- **THEN** the helper `nullStringFromEmpty` (or equivalent) SHALL convert it to `sql.NullString{Valid: false}` before binding to the SQL statement
- **AND** the resulting row SHALL store SQL NULL in that column, not the empty string

#### Scenario: Coverage extends to every currently-nullable users column

- **WHEN** auditing `scanUser`
- **THEN** `preferred_language`, `country`, `time_zone`, and `safe_address` SHALL each be read via one of the two accepted NULL-safe patterns
- **AND** any future addition of a nullable column to `users` SHALL adopt one of the same two patterns (enforced by code review)

### Requirement: Guest Language as Observable Store State

The guest (anonymous-period) language preference SHALL be owned by `UserStore`
as observable state, unified with the authenticated `User.preferredLanguage`
source. The frontend SHALL NOT read the active guest language through an
unobservable `I18N.getLocale()` call at render time for the purpose of driving
UI state; bindings that depend on the current language SHALL depend on the
store's observable value.

#### Scenario: Guest language exposed as observable
- **WHEN** a guest's preferred language is read for display or selection state
- **THEN** it SHALL be sourced from `UserStore`'s observable current-language
  value (backed by the anonymous-period `language` localStorage key)
- **AND** a change to the guest language SHALL notify dependent bindings so they
  re-evaluate without a manual mirror or a render-time `I18N.getLocale()` read

#### Scenario: Unified resolution across auth states
- **WHEN** the current preferred language is read
- **THEN** `UserStore` SHALL surface `User.preferredLanguage` for an
  authenticated user and the anonymous-period language for a guest
- **AND** callers SHALL NOT branch on `auth.isAuthenticated` to choose the source

### Requirement: UserStore Handles NULL Server Preferred Language

`UserStore` SHALL handle an authenticated user whose backend
`preferred_language` is NULL (historical rows not yet backfilled). This path is
independent of the guest-data reconciliation, which only fires when guest data
is present in localStorage.

#### Scenario: NULL preferred_language surfaced and backfilled
- **WHEN** the authenticated user's `User.preferredLanguage` is NULL
- **THEN** `UserStore` SHALL surface `I18N.getLocale()` as the effective language
- **AND** `UserStore` SHALL backfill the server value via
  `UpdatePreferredLanguage`, preserving the current `user-hydration-task`
  behavior
- **AND** this SHALL occur whether or not any guest data exists in localStorage

