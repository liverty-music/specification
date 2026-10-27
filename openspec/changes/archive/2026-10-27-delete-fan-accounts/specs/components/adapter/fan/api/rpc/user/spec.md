## MODIFIED Requirements

### Requirement: Per-user calls act only on the caller's own account

Get, Update, SetPreferredLanguage, SetHome, ResendEmailVerification, ListDeletionBlockers and Delete SHALL name no User: the request carries no User id, and each call acts on the signed-in caller's own User. Get, Update, SetPreferredLanguage, SetHome, ListDeletionBlockers and Delete SHALL resolve the caller's User from the caller's sign-in identity through UserUseCase.ResolveCaller and return its failure unchanged, NotFound when the caller has no User, before any other read or any change. ResendEmailVerification leaves resolving the caller to UserUseCase.ResendEmailVerification.

#### Scenario: Own account

- **WHEN** a signed-in caller calls Get, SetPreferredLanguage or SetHome
- **THEN** the call proceeds for the caller's User

#### Scenario: Another user's account

- **WHEN** a signed-in caller wants to read or change another User's account
- **THEN** no user service call accepts that User, and every call reads or changes only the caller's own User

#### Scenario: Missing user id

- **WHEN** a signed-in caller calls Get, SetPreferredLanguage or SetHome, whose requests carry no User id
- **THEN** the call acts on the caller's own User and does not fail for a missing User id

#### Scenario: Caller has no account

- **WHEN** the signed-in caller's identity has no User
- **THEN** the call fails with NotFound

#### Scenario: Deleting only oneself

- **WHEN** a signed-in caller calls Delete
- **THEN** only the caller's own User can be deleted, and no request names another User

## ADDED Requirements

### Requirement: ListDeletionBlockers returns what stops the caller's deletion

ListDeletionBlockers SHALL run UserUseCase.ListDeletionBlockers for the caller's User and return each blocker's kind and count, or no blocker; errors from the usecase SHALL be returned unchanged.

#### Scenario: Caller holds an upcoming ticket

- **WHEN** a signed-in caller holding an Issued Ticket for an Event next week calls ListDeletionBlockers
- **THEN** the response carries one Upcoming ticket blocker with count 1

#### Scenario: Nothing in progress

- **WHEN** a signed-in caller with no blocker calls ListDeletionBlockers
- **THEN** the response carries no blocker

### Requirement: Delete requires a sign-in within the last 5 minutes

Delete SHALL carry a proof of sign-in issued by the platform's sign-in service to the fan app. It SHALL fail with InvalidArgument, before any usecase runs, when the proof is missing. It SHALL fail with PermissionDenied, removing nothing, when the proof is not validly signed, was issued to another app, names an identity other than the caller's, or shows a sign-in older than 5 minutes. Otherwise it SHALL run UserUseCase.Delete for the caller's User and return an empty response; errors from the usecase SHALL be returned unchanged, so a caller with a blocker fails with FailedPrecondition.

#### Scenario: Fresh sign-in

- **WHEN** a caller with no blocker calls Delete with a proof of their own sign-in 2 minutes ago
- **THEN** UserUseCase.Delete runs for the caller's User and the call succeeds

#### Scenario: Old sign-in

- **WHEN** a caller calls Delete with a proof showing a sign-in 3 days ago
- **THEN** Delete fails with PermissionDenied and the User remains

#### Scenario: Proof of another identity

- **WHEN** a caller calls Delete with a fresh proof that names a different identity
- **THEN** Delete fails with PermissionDenied and the User remains

#### Scenario: No proof

- **WHEN** a caller calls Delete without a proof of sign-in
- **THEN** Delete fails with InvalidArgument and no usecase runs

#### Scenario: Caller with an upcoming ticket

- **WHEN** a caller holding an Issued Ticket for an Event next week calls Delete with a proof of their own sign-in 2 minutes ago
- **THEN** Delete fails with FailedPrecondition and the User remains
