## ADDED Requirements

### Requirement: Handlers return NotFound when user record does not exist
If `GetByExternalID` returns no user (e.g., user has a valid JWT but no record in `users`), the handler SHALL return `CodeNotFound`.

#### Scenario: Valid JWT but no user record
- **WHEN** an authenticated request arrives but `GetByExternalID` finds no matching user
- **THEN** the handler returns `connect.CodeNotFound` with message "user not found"
