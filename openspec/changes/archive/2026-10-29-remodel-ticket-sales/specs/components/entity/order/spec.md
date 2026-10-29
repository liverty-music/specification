# Spec Delta

## ADDED Requirements

### Requirement: A new Order is Pending

An Order SHALL be created Pending when a fan applies for tickets, before any payment, with its amount fixed at its seat type's amount for its ticket count. A Pending Order SHALL have no provider payment ID and no pay time.

#### Scenario: New order
- **WHEN** a fan applies for 2 tickets of a TicketStock whose seat type is priced 8000 yen
- **THEN** the Order is Pending, its amount is 16000 yen and it has no provider payment ID, pay time or provider refund ID

### Requirement: Ticket count fits the event

An Order's ticket count SHALL be at least 1 and at most the per-account limit of its TicketStock's event.

#### Scenario: Count within the limit
- **WHEN** the event's per-account limit is 4 and the ticket count is 2
- **THEN** the count is valid

#### Scenario: Zero tickets
- **WHEN** the ticket count is 0
- **THEN** the count is invalid

#### Scenario: Count over the limit
- **WHEN** the event's per-account limit is 4 and the ticket count is 5
- **THEN** the count is invalid

### Requirement: Paid only with a captured payment

An Order SHALL be Paid only with its card authorization, its provider payment ID and its pay time.

#### Scenario: Paid order
- **WHEN** an Order has a card authorization, a provider payment ID and a pay time
- **THEN** it can be Paid

#### Scenario: Paid without a payment
- **WHEN** an Order has no provider payment ID
- **THEN** it cannot be Paid

### Requirement: Void only from Pending

An Order SHALL become Void only from Pending, when its source ends without it ever being paid.

#### Scenario: Pending order
- **WHEN** the status is Pending
- **THEN** the Order can become Void

#### Scenario: Paid order
- **WHEN** the status is Paid
- **THEN** the Order cannot become Void

## MODIFIED Requirements

### Requirement: An Order has exactly one source

An Order SHALL be applied for through exactly one source: one LotteryEntry or one Checkout that names it. An Order that both a LotteryEntry and a Checkout name, or that neither names, SHALL be invalid.

#### Scenario: Order from a checkout

- **WHEN** a Checkout names an Order and no LotteryEntry does
- **THEN** its source is valid

#### Scenario: Order from a won lottery entry

- **WHEN** a LotteryEntry names an Order and no Checkout does
- **THEN** its source is valid

#### Scenario: Two sources

- **WHEN** a LotteryEntry and a Checkout name the same Order
- **THEN** the Order is invalid

## REMOVED Requirements

### Requirement: An Order is created Paid

**Reason**: An Order is now created when the fan applies, Pending, and becomes Paid when its payment is captured.
**Migration**: See "A new Order is Pending" and "Paid only with a captured payment"; existing Orders are deleted with the rest of the Organizer sales' data (design "Migration Plan").
