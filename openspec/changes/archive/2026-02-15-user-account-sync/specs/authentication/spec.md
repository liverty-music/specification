## MODIFIED Requirements

### Requirement: User ID Propagation

The system SHALL extract the user ID from validated tokens and propagate it through the request context.

**Rationale**: Handlers need access to the authenticated user ID to scope operations correctly (e.g., following artists, viewing followed content). The `external_id` (Zitadel `sub`) enables identity resolution against the local database.

#### Scenario: Authenticated Request

- **WHEN** a JWT token is successfully validated
- **THEN** the system extracts the user ID from the token's `sub` claim
- **AND** adds the user ID to the request context as `external_id`
- **AND** makes the user ID accessible to downstream handlers
