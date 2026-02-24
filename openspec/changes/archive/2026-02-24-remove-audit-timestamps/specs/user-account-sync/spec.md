## MODIFIED Requirements

### Requirement: User Account Provisioning on Signup

The system SHALL create a local user record in the application database when a user completes registration via Zitadel, linking the Zitadel identity (`sub` claim) to the local record via an `external_id` field (TEXT type).

#### Scenario: Successful signup provisioning

- **WHEN** a user completes registration via Zitadel and the frontend receives the OIDC callback with `state.isRegistration === true`
- **THEN** the frontend SHALL call the `Create` RPC with the user's `email` parameter only
- **AND** the backend SHALL extract `external_id` (from JWT `sub` claim) and `name` (from JWT `name` claim)
- **AND** the backend SHALL create a new user record with `external_id`, `email`, and `name` persisted
- **AND** the backend SHALL return the created user without any `create_time` field

## REMOVED Requirements

### Requirement: User Create Time Tracking

**Reason**: `create_time` is a metadata timestamp not used by any business logic. Audit logging will be handled separately.
**Migration**: Remove `create_time` from `User` protobuf entity. Reserve field number 3 in `user.proto`. Remove `created_at` and `updated_at` columns from `users` table.
