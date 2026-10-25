## MODIFIED Requirements

### Requirement: Refund announced

For each listing it refunds, and for each listing from ResaleListing.ListSoldUnrefunded that has a refund time and no sold email send time, RefundSold SHALL announce that the listing was refunded, carrying the listing, its user, its Order and its event. Each announcement is a new message; consumers SHALL treat a repeated announcement of a listing as one. A failed announcement SHALL NOT stop the other listings and is made again on the next run; the refund is not repeated.

#### Scenario: Refund announced
- **WHEN** a listing is refunded
- **THEN** the refund is announced once with the listing, its user, its Order and its event

#### Scenario: Announcement fails
- **WHEN** announcing a refunded listing fails
- **THEN** the next run announces it again and does not refund it again

#### Scenario: Email already sent
- **WHEN** a refunded listing has a sold email send time
- **THEN** it is not announced again
