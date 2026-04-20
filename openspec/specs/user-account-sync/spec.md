## MODIFIED Requirements

### Requirement: User Account Provisioning on Signup

The system SHALL create a local user record in the application database when a user completes the onboarding tutorial and authenticates via Passkey. The provisioning is triggered by the guest data merge process at the end of the tutorial.

The `UserService.Create` RPC SHALL be idempotent on duplicate `external_id`: a second call for the same `external_id` SHALL return the existing user as a successful response rather than `connect.CodeAlreadyExists`. This allows the frontend to treat `Create` as a uniform "resolve-or-provision" bootstrap RPC on any device, regardless of whether the user was provisioned in a prior session.

#### Scenario: Successful signup provisioning from tutorial

- **WHEN** a user completes Passkey authentication at tutorial Step 6
- **AND** the frontend has no cached `user_id` for the authenticated `external_id`
- **THEN** the frontend SHALL call the `Create` RPC with the user's `email` parameter
- **AND** the backend SHALL extract `external_id` (from JWT `sub` claim) and `name` (from JWT `name` claim)
- **AND** the backend SHALL create a new user record with `external_id`, `email`, and `name` persisted
- **AND** the backend SHALL return the newly created `User` entity in `CreateResponse.user`
- **AND** the frontend SHALL cache the returned `user_id` in `localStorage` keyed by `external_id`
- **AND** the frontend SHALL then proceed to sync guest data (follows, passion levels)

#### Scenario: Successful provisioning from Login link

- **WHEN** a returning user authenticates via the [Login] link on the LP
- **AND** the frontend has no cached `user_id` for the authenticated `external_id` (e.g., fresh device or cleared storage)
- **THEN** the frontend SHALL call the `Create` RPC with the user's `email` parameter
- **AND** the backend SHALL either create a new record (first-ever sign-in) or return the existing record (returning user)
- **AND** the frontend SHALL cache the returned `user_id` in `localStorage` keyed by `external_id`

#### Scenario: Duplicate Create call returns the existing user idempotently

- **WHEN** the `Create` RPC is called with an `external_id` that already exists in the database
- **THEN** the backend SHALL return `OK` with `CreateResponse.user` populated from the existing row
- **AND** the backend SHALL NOT return `connect.CodeAlreadyExists`
- **AND** the backend SHALL NOT modify the existing `email` or `name` fields (the duplicate call is a read, not an upsert)
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
