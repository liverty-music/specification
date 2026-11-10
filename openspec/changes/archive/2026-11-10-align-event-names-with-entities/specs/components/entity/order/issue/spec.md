## MODIFIED Requirements

### Requirement: An issued Order is announced as paid

Issue SHALL announce the Order as paid (Order.Paid), carrying it in status Paid, together with what it changes: all of it is stored and announced, or nothing is. An Issue that fails, including with AlreadyExists, SHALL announce nothing. When the announcement cannot be recorded, Issue SHALL fail with Unavailable and change nothing. The paid announcement is what product analytics records as one "order paid" signal for the Order, at its pay time.

#### Scenario: Order paid

- **WHEN** Issue makes the Pending Order of a fan's Checkout of 2 tickets Paid
- **THEN** the Order is announced as paid once

#### Scenario: Order already paid

- **WHEN** Issue fails with AlreadyExists because the Order is already Paid
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** the paid announcement of an Order cannot be recorded
- **THEN** Issue fails with Unavailable, the Order stays Pending, no Ticket is stored and the Checkout stays Committed

### Requirement: Issue a won resale entry's Order with its listings

When the Order's source is a Won ResaleEntry, Issue SHALL also, in the same indivisible step as making the Order Paid with its Tickets and Settlement: make each ResaleListing allocated to the entry Sold with the time of issuance, make the Ticket of each Voided, and have the Settlement of each Order those Tickets came from give up the share of its resold tickets. It SHALL announce each listing it makes Sold as sold (ResaleListing.Sold), carrying the listing as Sold, together with the rest of the change. It SHALL fail with FailedPrecondition, changing nothing, when the entry is not Won or one of its listings is not allocated to it.

#### Scenario: Order issued from a won resale entry
- **WHEN** Issue is called with an Order of 1 Ticket whose source is a Won ResaleEntry allocated a listing of another fan's Ticket, from that fan's Order of 2 Tickets with a Held split of 9500 yen
- **THEN** the Order is Paid with its Ticket and Settlement, the listing is Sold and announced as sold, the other fan's Ticket is Voided and their Order's split is 4750 yen

#### Scenario: Entry no longer won
- **WHEN** the source ResaleEntry is Lost
- **THEN** Issue fails with FailedPrecondition and nothing changes
