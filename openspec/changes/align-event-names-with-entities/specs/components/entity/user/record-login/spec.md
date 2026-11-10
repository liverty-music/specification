## MODIFIED Requirements

### Requirement: A recorded sign-in is announced with the change

When RecordLogin changes the last login time, it SHALL announce the User as signed in (User.SignedIn), with its new last login time, together with the change: both are stored or neither is. Product analytics SHALL record each such announcement as one sign-in of the User at that time. When the announcement cannot be recorded, RecordLogin SHALL fail with Unavailable and the last login time SHALL stay as it was.

#### Scenario: Sign-in announced

- **WHEN** RecordLogin changes a User's last login time to 2026-10-28 12:00 JST
- **THEN** one sign-in is announced, carrying the User with last login time 2026-10-28 12:00 JST, and product analytics records one sign-in

#### Scenario: Announcement cannot be recorded

- **WHEN** RecordLogin would change the last login time and the announcement cannot be recorded
- **THEN** RecordLogin fails with Unavailable and the last login time is unchanged
