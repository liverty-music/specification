# Order.Issue

## Purpose

Makes a Pending Order Paid together with the Tickets it issues and its Settlement.

## Requirements

### Requirement: Issue makes a pending order paid with its tickets and settlement

Issue SHALL, together or not at all:
- make the Pending Order Paid with its captured payment: provider payment ID, payment method, card brand, card last four and pay time;
- store all of its Tickets;
- store a Held Settlement for the Order's event and Organizer, with one split paying that Organizer its net share of the Order's amount after the platform fee at the Organizer's platform fee rate;
- when the Order's source is a Checkout, make that Checkout Completed.

It SHALL fail with AlreadyExists when the Order is already Paid or Refunded, and with FailedPrecondition when it is Void. When the source is a Checkout, it SHALL fail with FailedPrecondition, changing nothing, unless that Checkout is Committed and has a capture time.

#### Scenario: Order issued

- **WHEN** Issue is called with a Pending Order, its 3 Tickets, and a Settlement for the event's Organizer
- **THEN** the Order is Paid, and the 3 Tickets and a Held Settlement with one Organizer split are stored

#### Scenario: Order issued from a checkout

- **WHEN** Issue is called with a Pending Order whose source is a Committed, charged Checkout
- **THEN** the Order is Paid, its Tickets are stored and the Checkout is Completed

#### Scenario: Checkout not charged

- **WHEN** the source Checkout is Committed but has no capture time
- **THEN** Issue fails with FailedPrecondition and changes nothing

#### Scenario: Failure stores nothing

- **WHEN** storing any Ticket or the Settlement fails
- **THEN** the Order stays Pending, no Ticket or Settlement is stored, and a Checkout stays Committed

#### Scenario: Second order for the lottery entry

- **WHEN** a LotteryEntry's Order is already Paid
- **THEN** Issue fails with AlreadyExists and changes nothing

#### Scenario: Second order for the checkout

- **WHEN** a Checkout's Order is already Paid
- **THEN** Issue fails with AlreadyExists and changes nothing

#### Scenario: Void order

- **WHEN** the Order is Void
- **THEN** Issue fails with FailedPrecondition and changes nothing

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
