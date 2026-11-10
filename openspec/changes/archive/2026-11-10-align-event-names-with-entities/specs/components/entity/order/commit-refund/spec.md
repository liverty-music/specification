## MODIFIED Requirements

### Requirement: A recorded refund is announced with it

When CommitRefund makes the Order Refunded, it SHALL announce the Order as refunded (Order.Refunded) together with the refund: both are stored or neither is. When the Order is already Refunded, CommitRefund SHALL announce nothing. When the announcement cannot be recorded, CommitRefund SHALL fail with Unavailable and change nothing.

#### Scenario: Refund announced
- **WHEN** CommitRefund makes a Paid Order Refunded
- **THEN** the Order is announced as refunded once

#### Scenario: Recorded twice
- **WHEN** CommitRefund is called again for an Order that is already Refunded
- **THEN** nothing is announced and the first refund's reason, amount and time are kept

#### Scenario: Announcement cannot be recorded
- **WHEN** the refund announcement cannot be recorded
- **THEN** CommitRefund fails with Unavailable and the Order stays Paid
