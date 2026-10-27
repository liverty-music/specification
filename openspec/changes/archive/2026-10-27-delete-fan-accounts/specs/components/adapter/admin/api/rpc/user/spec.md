## MODIFIED Requirements

### Requirement: Only admins remove users

Every request SHALL carry a valid sign-in, or fail with Unauthenticated, and the caller SHALL hold the admin role, or the request fails with PermissionDenied and has no effect. This holds for Delete and GetByEmail alike.

#### Scenario: Not signed in

- **WHEN** Delete is called without a valid sign-in
- **THEN** it fails with Unauthenticated and the User remains

#### Scenario: Non-admin

- **WHEN** a signed-in caller without the admin role calls Delete
- **THEN** it fails with PermissionDenied and the User remains

#### Scenario: Non-admin looks up a user

- **WHEN** a signed-in caller without the admin role calls GetByEmail
- **THEN** it fails with PermissionDenied and no User is returned

## ADDED Requirements

### Requirement: GetByEmail returns a user with its deletion blockers

GetByEmail SHALL fail with InvalidArgument, before any usecase runs, when the email address is missing or not a well-formed address of at most 165 characters. Otherwise it SHALL run UserUseCase.GetByEmail and then UserUseCase.ListDeletionBlockers for the returned User, and return the User's id, email and name together with each blocker's kind and count. Errors from either usecase SHALL be returned unchanged, so an unregistered address fails with NotFound.

#### Scenario: Admin finds a fan

- **WHEN** an admin calls GetByEmail with the address of a fan who holds two Tickets for an Event next week
- **THEN** the response carries that User's id, email and name and one Upcoming ticket blocker with count 2

#### Scenario: Fan with nothing in progress

- **WHEN** an admin calls GetByEmail with the address of a fan with no blocker
- **THEN** the response carries the User and no blocker

#### Scenario: Unregistered address

- **WHEN** no User has the address
- **THEN** GetByEmail fails with NotFound

#### Scenario: Malformed address

- **WHEN** GetByEmail is called with `not-an-address`
- **THEN** it fails with InvalidArgument and no usecase runs
