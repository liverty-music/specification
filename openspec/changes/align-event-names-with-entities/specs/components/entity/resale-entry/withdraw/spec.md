## MODIFIED Requirements

### Requirement: A withdrawn entry is announced with the change

When Withdraw makes an entry Withdrawn, it SHALL announce the entry as withdrawn (ResaleEntry.Withdrawn), as it is after the change, together with the change: both are stored or neither is. When Withdraw fails it SHALL announce nothing. When the announcement cannot be recorded, Withdraw SHALL fail with Unavailable, and the entry SHALL stay Entered and its Order Pending.

#### Scenario: Withdrawal announced
- **WHEN** an Entered entry is withdrawn
- **THEN** the entry is announced as withdrawn once, carrying it as Withdrawn

#### Scenario: Announcement cannot be recorded
- **WHEN** the announcement of a withdrawal cannot be recorded
- **THEN** Withdraw fails with Unavailable, the entry stays Entered and its Order stays Pending
