# components/adapter/admin/api/rpc/user Specification

## Purpose
The admin-facing User service boundary: only admins remove a fan User, the boundary validates the request, and it runs UserUseCase.Delete.

## Requirements

### Requirement: Only admins remove users

Every request SHALL carry a valid sign-in, or fail with Unauthenticated, and the caller SHALL hold the admin role, or the request fails with PermissionDenied and has no effect.

#### Scenario: Not signed in

- **WHEN** Delete is called without a valid sign-in
- **THEN** it fails with Unauthenticated and the User remains

#### Scenario: Non-admin

- **WHEN** a signed-in caller without the admin role calls Delete
- **THEN** it fails with PermissionDenied and the User remains

### Requirement: Delete runs UserUseCase.Delete

Delete SHALL fail with InvalidArgument, before any usecase runs, when the UserId is missing or not a UUID. Otherwise it SHALL run UserUseCase.Delete with the UserId and return an empty response; errors from the usecase SHALL be returned unchanged.

#### Scenario: Admin removes a test user

- **WHEN** an admin calls Delete with a fan User's id
- **THEN** UserUseCase.Delete runs and the call succeeds

#### Scenario: Missing UserId

- **WHEN** Delete is called without a UserId
- **THEN** it fails with InvalidArgument and no usecase runs

#### Scenario: User holds a ticket

- **WHEN** UserUseCase.Delete fails with FailedPrecondition
- **THEN** Delete fails with FailedPrecondition
