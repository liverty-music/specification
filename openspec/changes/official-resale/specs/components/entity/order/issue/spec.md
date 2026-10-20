## MODIFIED Requirements

### Requirement: Order, tickets and settlement together, once per source

Issue SHALL store, together or not at all:
- the Order;
- all of its Tickets;
- a Held Settlement for the Order's event and Organizer, with one split paying that Organizer its net share of the Order's amount after the platform fee at the Organizer's platform fee rate;
- when the Order's source is a Checkout, that Checkout made Completed;
- when that Checkout is a resale Checkout: each ResaleListing it holds made Sold with the time of issuance, the Ticket of each made Voided, and the Settlement of each Order those Tickets came from given up the share of its resold tickets.

It SHALL fail with AlreadyExists when an Order already exists for the same source. When the source is a Checkout, it SHALL fail with FailedPrecondition, storing nothing, unless that Checkout is Committed and has a capture time.

#### Scenario: Order issued

- **WHEN** Issue is called with an Order, its 3 Tickets, and a Settlement for the event's Organizer
- **THEN** the Order, the 3 Tickets and a Held Settlement with one Organizer split are stored

#### Scenario: Order issued from a checkout

- **WHEN** Issue is called with an Order whose source is a Committed, charged Checkout
- **THEN** the Order and its Tickets are stored and the Checkout is Completed

#### Scenario: Order issued from a resale checkout

- **WHEN** Issue is called with an Order of 1 Ticket whose source is a charged resale Checkout holding a listing of another fan's Ticket, from that fan's Order of 2 Tickets with a Held split of 9500 yen
- **THEN** the Order, its Ticket and its Settlement are stored, the listing is Sold, the other fan's Ticket is Voided and their Order's split is 4750 yen

#### Scenario: Checkout not charged

- **WHEN** the source Checkout is Committed but has no capture time
- **THEN** Issue fails with FailedPrecondition and stores nothing

#### Scenario: Failure stores nothing

- **WHEN** storing any Ticket or the Settlement fails
- **THEN** neither the Order, any Ticket nor the Settlement is stored, no listing is Sold, no Ticket is Voided, and a Checkout stays Committed

#### Scenario: Second order for the lottery entry

- **WHEN** an Order already exists for the LotteryEntry
- **THEN** Issue fails with AlreadyExists and stores nothing

#### Scenario: Second order for the checkout

- **WHEN** an Order already exists for the Checkout
- **THEN** Issue fails with AlreadyExists and stores nothing
