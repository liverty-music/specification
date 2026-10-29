## ADDED Requirements

### Requirement: A reverted commit is announced with the change

When RevertCommit makes a Checkout Released, it SHALL announce it as released, carrying the Checkout as it is after the change, together with the change: both are stored or neither is. When it changes nothing it SHALL announce nothing. When the announcement cannot be recorded, RevertCommit SHALL fail with Unavailable and change nothing.

#### Scenario: Commit reverted
- **WHEN** RevertCommit makes a Committed Checkout without a capture time Released
- **THEN** one checkout release is announced, carrying the Checkout as Released

#### Scenario: Announcement cannot be recorded
- **WHEN** the announcement cannot be recorded
- **THEN** RevertCommit fails with Unavailable and the Checkout stays Committed
