<!-- spec: id-resolution | target: components/entity/user | flags: CLASSNAME | new_name: Handlers return NotFound when user record does not exist -->

### Requirement: Handlers return NotFound when user record does not exist
If `GetByExternalID` returns no user (e.g., user has a valid JWT but no record in `users`), the resolution layer SHALL return `CodeNotFound`.

#### Scenario: Valid JWT but no user record
- **WHEN** an authenticated request arrives but `GetByExternalID` finds no matching user
- **THEN** the handler or use case returns `connect.CodeNotFound` with message "user not found"
