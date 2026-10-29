# Spec Delta

## ADDED Requirements

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


## REMOVED Requirements

### Requirement: Order, tickets and settlement together, once per source

**Reason**: An Order is now created Pending when the fan applies, and Issue makes it Paid; buying another fan's listing moves to the change resell-tickets-by-lottery.
**Migration**: See "Issue makes a pending order paid with its tickets and settlement".
