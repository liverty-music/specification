# Create

## Purpose

Provisions a backend account for a newly authenticated user, resolving or creating their user record and capturing their home area and preferred display language at signup.

## Requirements

### Requirement: User Account Provisioning on Signup

The system SHALL create a local user record in the application database when a user completes the onboarding tutorial and authenticates via Passkey. The provisioning is triggered by the guest data merge process at the end of the tutorial.

The `UserService.Create` RPC SHALL be idempotent on duplicate `external_id`: a second call for the same `external_id` SHALL return the existing user as a successful response rather than `connect.CodeAlreadyExists`. This allows the frontend to treat `Create` as a uniform "resolve-or-provision" bootstrap RPC on any device, regardless of whether the user was provisioned in a prior session.

The `Create` RPC SHALL carry the user's effective locale as `preferred_language` so the language preference is persisted atomically with the new user row. On the idempotent-return path, `preferred_language` SHALL NOT overwrite an existing row's value (mirroring the rule for `home`).

#### Scenario: Successful signup provisioning from tutorial

- **WHEN** a user completes Passkey authentication at tutorial Step 6
- **AND** the frontend has no cached `user_id` for the authenticated `external_id`
- **THEN** the frontend SHALL call the `Create` RPC with the user's `email` parameter AND `preferred_language` set to `I18N.getLocale()` (the locale currently effective in the client)
- **AND** the backend SHALL extract `external_id` (from JWT `sub` claim) and `name` (from JWT `name` claim)
- **AND** the backend SHALL create a new user record with `external_id`, `email`, `name`, and `preferred_language` persisted
- **AND** the backend SHALL return the newly created `User` entity in `CreateResponse.user` (including `preferred_language`)
- **AND** the frontend SHALL cache the returned `user_id` in `localStorage` keyed by `external_id`
- **AND** the frontend SHALL remove `localStorage['language']` after the successful Create
- **AND** the frontend SHALL then proceed to sync guest data (follows, passion levels)

#### Scenario: Successful provisioning from Login link

- **WHEN** a returning user authenticates via the [Login] link on the LP
- **AND** the frontend has no cached `user_id` for the authenticated `external_id` (e.g., fresh device or cleared storage)
- **THEN** the frontend SHALL call the `Create` RPC with the user's `email` parameter AND `preferred_language` set to `I18N.getLocale()`
- **AND** the backend SHALL either create a new record (first-ever sign-in) or return the existing record (returning user)
- **AND** the frontend SHALL cache the returned `user_id` in `localStorage` keyed by `external_id`
- **AND** the frontend SHALL remove `localStorage['language']` after the successful Create

#### Scenario: Duplicate Create call returns the existing user idempotently

- **WHEN** the `Create` RPC is called with an `external_id` that already exists in the database
- **THEN** the backend SHALL return `OK` with `CreateResponse.user` populated from the existing row
- **AND** the backend SHALL NOT return `connect.CodeAlreadyExists`
- **AND** the backend SHALL NOT modify the existing `email`, `name`, `home`, or `preferred_language` fields (the duplicate call is a read, not an upsert)
- **AND** the frontend SHALL treat the response identically to a fresh creation — cache the `user_id` and proceed

#### Scenario: Cached userID is reused on subsequent boots

- **WHEN** the app boots for a user whose `external_id` has a cached `user_id` in `localStorage`
- **THEN** the frontend SHALL read the cached `user_id` **before** issuing any authenticated per-user RPC
- **AND** the frontend SHALL call `UserService.Get` with the cached `user_id` to hydrate the current profile
- **AND** the backend SHALL verify the supplied `user_id` matches the JWT-derived userID (per `rpc-auth-scoping`)

#### Scenario: Cached userID is cleared on sign-out

- **WHEN** the user signs out via the auth service
- **THEN** the frontend SHALL remove the `localStorage` entry keyed by the signed-out user's `external_id`
- **AND** the next sign-in SHALL follow the cache-miss path (call `Create` to resolve the `user_id`)

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
