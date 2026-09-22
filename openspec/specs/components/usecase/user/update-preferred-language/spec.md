# Update Preferred Language

## Purpose

Persists each authenticated user's display language in the backend database so language is consistent across devices and browser sessions. Defines the proto-surface (entity field, Create capture, UpdatePreferredLanguage RPC), the storage semantics (NULL = "not yet set by client"), and the repository scan contract that prevents NULL-column reads from masquerading as `not_found` / `already_exists` at the wire boundary.

## Requirements

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
