# Spec Delta

## ADDED Requirements

### Requirement: A checkout holds for 15 minutes

A new Checkout SHALL start Held, with a hold expiry 15 minutes after its create time.

#### Scenario: New checkout
- **WHEN** a fan starts a checkout at 18:00
- **THEN** the Checkout is Held and its hold expires at 18:15

### Requirement: Sale of a checkout

A Checkout SHALL belong to a FirstCome TicketSale that names the event of its Order's TicketStock. It holds that TicketStock's tickets and nothing else.

#### Scenario: First-come sale of the event
- **WHEN** a Checkout belongs to a FirstCome sale that names the event of its Order's TicketStock
- **THEN** it is valid

#### Scenario: Lottery sale
- **WHEN** a Checkout belongs to a Lottery sale
- **THEN** it is invalid

#### Scenario: No sale
- **WHEN** a Checkout belongs to no TicketSale
- **THEN** it is invalid

## MODIFIED Requirements

### Requirement: Holding

A Checkout SHALL be holding at a time when it is Held and the time is before its hold expiry. Only holding Checkouts count in a TicketStock's held count, and only a holding Checkout can be committed.

#### Scenario: Within the hold
- **WHEN** a Held Checkout expiring at 18:15 is checked at 18:14
- **THEN** it is holding

#### Scenario: Hold lapsed
- **WHEN** a Held Checkout expiring at 18:15 is checked at 18:15
- **THEN** it is not holding

## REMOVED Requirements

### Requirement: A new checkout holds for 15 minutes

**Reason**: The amount moved to the Order, and a Checkout no longer buys resale tickets, so a resale hold expiry no longer exists.
**Migration**: See "A checkout holds for 15 minutes"; the amount is on the Order ("A new Order is Pending").

### Requirement: A resale checkout holds listings

**Reason**: A Checkout only buys a FirstCome sale's stock. Official resale is bought through its own lottery, added by the change resell-tickets-by-lottery.
**Migration**: None in this change; existing resale Checkouts are deleted with the rest of the Organizer sales' data (design "Migration Plan").
