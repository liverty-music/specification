## ADDED Requirements

### Requirement: A recorded refund is announced with it

When RecordRefund sets the refund, it SHALL announce the ResaleListing as refunded together with the refund: both are stored or neither is. When the listing already has a refund time, RecordRefund SHALL announce nothing. When the announcement cannot be recorded, RecordRefund SHALL fail with Unavailable and set nothing.

#### Scenario: Refund announced
- **WHEN** RecordRefund sets the refund of a Sold listing
- **THEN** the listing is announced as refunded once

#### Scenario: Recorded twice
- **WHEN** RecordRefund is called again for a listing that has a refund time
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded
- **WHEN** the refund announcement cannot be recorded
- **THEN** RecordRefund fails with Unavailable and the listing has no refund time
