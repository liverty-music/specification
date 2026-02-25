## MODIFIED Requirements

### Requirement: User Account Provisioning on Signup

The system SHALL create a local user record in the application database when a user completes registration via Zitadel, linking the Zitadel identity (`sub` claim) to the local record via an `external_id` field (TEXT type). The system SHALL support two provisioning paths: the primary frontend-driven Create RPC path, and a complementary Zitadel webhook path that enriches user data.

#### Scenario: Successful signup provisioning via Create RPC (primary path)

- **WHEN** a user completes registration via Zitadel and the frontend receives the OIDC callback with `state.isRegistration === true`
- **THEN** the frontend SHALL call the `Create` RPC with the user's `email` parameter only
- **AND** the backend SHALL extract `external_id` (from JWT `sub` claim) and `name` (from JWT `name` claim)
- **AND** the backend SHALL create a new user record with `external_id`, `email`, and `name` persisted
- **AND** the backend SHALL return the created user

#### Scenario: Successful signup provisioning via Zitadel webhook (complementary path)

- **WHEN** a user completes registration via Zitadel
- **THEN** Zitadel SHALL send a `user.human.added` event to the backend webhook endpoint
- **AND** the backend SHALL UPSERT the user record with `external_id`, `email`, `name`, and `preferred_language` from the event payload
- **AND** the UPSERT SHALL enrich existing records without overwriting non-empty values with empty strings

#### Scenario: Duplicate provisioning attempt

- **WHEN** the `Create` RPC is called with an `external_id` that already exists in the database
- **THEN** the system SHALL return `connect.CodeAlreadyExists`
- **AND** the frontend SHALL handle this error gracefully (treat as success since the user already exists)
