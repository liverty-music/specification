## ADDED Requirements

### Requirement: An expired Checkout is announced with the change

When Release makes a Checkout Expired, it SHALL announce the Checkout as expired, carrying it in status Expired, together with the change: both are stored or neither is. When Release changes nothing, it SHALL announce nothing. When the announcement cannot be recorded, Release SHALL fail with Unavailable and the Checkout SHALL stay Held.

#### Scenario: Hold lapsed

- **WHEN** a Held Checkout expiring at 18:15 is released at 18:16
- **THEN** one checkout expiry is announced, carrying the Checkout as Expired

#### Scenario: Nothing to release

- **WHEN** Release is called for a Checkout that is Committed, Completed, already Expired or still holding
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** a Held Checkout whose hold lapsed is released and the announcement cannot be recorded
- **THEN** Release fails with Unavailable and the Checkout stays Held
