## MODIFIED Requirements

### Requirement: User Account Provisioning on Signup

The system SHALL create a local user record in the application database when a user completes the onboarding tutorial and authenticates via Passkey. The provisioning is triggered by the guest data merge process at the end of the tutorial.

#### Scenario: Successful signup provisioning from tutorial

- **WHEN** a user completes Passkey authentication at tutorial Step 6
- **THEN** the frontend SHALL call `UserService/Get` to check for an existing user record
- **AND** if the backend returns `NOT_FOUND`, the frontend SHALL call the `Create` RPC with the user's `email` parameter
- **AND** the backend SHALL extract `external_id` (from JWT `sub` claim) and `name` (from JWT `name` claim)
- **AND** the backend SHALL create a new user record with `external_id`, `email`, and `name` persisted
- **AND** the frontend SHALL cache the `User` entity from the `CreateResponse.user` field without making an additional `Get` RPC call
- **AND** the frontend SHALL then proceed to sync guest data (follows, passion levels)

#### Scenario: Successful provisioning from Login link

- **WHEN** a returning user authenticates via the [Login] link on the LP
- **THEN** the frontend SHALL call `UserService/Get` to check for an existing user record
- **AND** if the backend returns `NOT_FOUND`, the frontend SHALL call the `Create` RPC with the user's `email` parameter
- **AND** the backend SHALL create the user record as normal
- **AND** the frontend SHALL cache the `User` entity from the `CreateResponse.user` field without making an additional `Get` RPC call

#### Scenario: Duplicate provisioning attempt

- **WHEN** the `Create` RPC is called with an `external_id` that already exists in the database
- **THEN** the system SHALL return `connect.CodeAlreadyExists`
- **AND** the frontend SHALL handle this error gracefully (treat as success since the user already exists)
- **AND** the frontend SHALL call `UserService/Get` to retrieve and cache the existing `User` entity
- **AND** the guest data merge SHALL proceed normally
