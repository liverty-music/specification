## Purpose

Stores the time a User last signed in, as the identity provider reported it, and announces the change so product analytics can count sign-ins.

## ADDED Requirements

### Requirement: RecordLogin keeps the latest sign-in time

RecordLogin SHALL take a User's id and a sign-in time, and SHALL set the User's last login time to that time when the User has no last login time or its last login time is earlier. When the stored last login time is the same as or later than the given time, RecordLogin SHALL succeed, change nothing and announce nothing. RecordLogin SHALL fail with NotFound and store nothing when no User has the id.

#### Scenario: First sign-in recorded

- **WHEN** RecordLogin runs for a User with no last login time and the time 2026-10-28 10:00 JST
- **THEN** the User's last login time is 2026-10-28 10:00 JST

#### Scenario: Later sign-in

- **WHEN** the User's last login time is 2026-10-28 10:00 JST and RecordLogin runs with 2026-10-28 12:00 JST
- **THEN** the User's last login time is 2026-10-28 12:00 JST

#### Scenario: Same or older sign-in

- **WHEN** the User's last login time is 2026-10-28 12:00 JST and RecordLogin runs with 2026-10-28 12:00 JST or 2026-10-28 10:00 JST
- **THEN** RecordLogin succeeds, the last login time stays 2026-10-28 12:00 JST and nothing is announced

#### Scenario: Unknown User

- **WHEN** no User has the id
- **THEN** RecordLogin fails with NotFound and nothing is stored

### Requirement: A recorded sign-in is announced with the change

When RecordLogin changes the last login time, it SHALL announce the User as signed in, with its new last login time, together with the change: both are stored or neither is. Product analytics SHALL record each such announcement as one sign-in of the User at that time. When the announcement cannot be recorded, RecordLogin SHALL fail with Unavailable and the last login time SHALL stay as it was.

#### Scenario: Sign-in announced

- **WHEN** RecordLogin changes a User's last login time to 2026-10-28 12:00 JST
- **THEN** one sign-in is announced, carrying the User with last login time 2026-10-28 12:00 JST, and product analytics records one sign-in

#### Scenario: Announcement cannot be recorded

- **WHEN** RecordLogin would change the last login time and the announcement cannot be recorded
- **THEN** RecordLogin fails with Unavailable and the last login time is unchanged
