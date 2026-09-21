# Capability: ID Resolution

## Purpose

Defines how authenticated RPC handlers resolve the Zitadel external ID (JWT `sub` claim) to the internal `users.id` UUID before any database access. This prevents raw external IDs from being passed to UUID columns and ensures consistent user identity across all services.

## Requirements

### Requirement: Handlers return NotFound when user record does not exist
If `GetByExternalID` returns no user (e.g., user has a valid JWT but no record in `users`), the resolution layer SHALL return `CodeNotFound`.

#### Scenario: Valid JWT but no user record
- **WHEN** an authenticated request arrives but `GetByExternalID` finds no matching user
- **THEN** the handler or use case returns `connect.CodeNotFound` with message "user not found"
