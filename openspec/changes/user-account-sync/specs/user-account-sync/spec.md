## ADDED Requirements

### Requirement: User Account Provisioning on Signup

The system SHALL create a local user record in the application database when a user completes registration via Zitadel, linking the Zitadel identity (`sub` claim) to the local record via an `external_id` field (UUID type).

#### Scenario: Successful signup provisioning

- **WHEN** a user completes registration via Zitadel and the frontend receives the OIDC callback with `state.isRegistration === true`
- **THEN** the frontend SHALL call the `Create` RPC with the user's `external_id` (Zitadel `sub`), `email`, and `name` from the JWT claims
- **AND** the backend SHALL create a new user record with `external_id` set to the Zitadel `sub`
- **AND** the backend SHALL return the created user

#### Scenario: Duplicate provisioning attempt

- **WHEN** the `Create` RPC is called with an `external_id` that already exists in the database
- **THEN** the system SHALL return `connect.CodeAlreadyExists`
- **AND** the frontend SHALL handle this error gracefully (treat as success since the user already exists)

### Requirement: External Identity Mapping

The system SHALL maintain a unique mapping between Zitadel identity (`sub` claim) and the local user record using a UUID-typed `external_id` column.

#### Scenario: Store external identity

- **WHEN** a new user record is created via `Create`
- **THEN** the `external_id` column SHALL be set to the Zitadel `sub` claim value (UUID)
- **AND** the `external_id` column SHALL have a UNIQUE constraint

#### Scenario: Lookup by external identity

- **WHEN** the system receives a request with a Zitadel `sub` claim
- **THEN** the system SHALL be able to find the corresponding local user by `external_id`

### Requirement: User Entity External ID Field

The `User` protobuf entity SHALL include an `external_id` field to represent the Zitadel identity link.

#### Scenario: External ID in User entity

- **WHEN** a `User` entity is serialized
- **THEN** it SHALL include the `external_id` field as a UUID string
- **AND** the field SHALL be validated as a UUID format via protovalidate

### Requirement: Create RPC with Email Parameter

The existing `Create` RPC SHALL accept `email` as a top-level parameter in the request. The `external_id` (Zitadel `sub` claim) SHALL be extracted from the authenticated JWT context by the backend.

#### Scenario: Create user with external identity

- **WHEN** `Create` is called with `email` by an authenticated user
- **THEN** the system SHALL extract `external_id` from the JWT `sub` claim
- **AND** create a new user record with both `email` and `external_id` persisted

#### Scenario: Missing required fields

- **WHEN** `Create` is called without `email`
- **THEN** the system SHALL return `connect.CodeInvalidArgument`

#### Scenario: Authentication required

- **WHEN** `Create` is called without a valid JWT token
- **THEN** the system SHALL return `connect.CodeUnauthenticated`
