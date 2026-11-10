## MODIFIED Requirements

### Requirement: An issued Order is announced as paid

Issue SHALL announce the Order as paid, carrying it in status Paid with its source — the LotteryEntry, Checkout or ResaleEntry that names it — together with what it changes: all of it is stored and announced, or nothing is. An Issue that fails, including with AlreadyExists, SHALL announce nothing. When the announcement cannot be recorded, Issue SHALL fail with Unavailable and change nothing. The paid announcement is what product analytics records as one "order paid" signal for the Order, at its pay time.

#### Scenario: Order paid

- **WHEN** Issue makes the Pending Order of a fan's Checkout of 2 tickets Paid
- **THEN** the Order is announced as paid once

#### Scenario: Order of a won resale entry paid

- **WHEN** Issue makes Paid the Pending Order of a Won ResaleEntry
- **THEN** the paid announcement carries the Order with that ResaleEntry as its source, not a LotteryEntry

#### Scenario: Order already paid

- **WHEN** Issue fails with AlreadyExists because the Order is already Paid
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** the paid announcement of an Order cannot be recorded
- **THEN** Issue fails with Unavailable, the Order stays Pending, no Ticket is stored and the Checkout stays Committed
