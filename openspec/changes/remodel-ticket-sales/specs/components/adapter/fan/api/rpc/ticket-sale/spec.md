# Spec Delta

## ADDED Requirements

### Requirement: A returned sale shows states, never counts

A TicketSale returned by the fan boundary SHALL carry its id, Series, name, method, start time, end time and verification requirement. Each TicketStock returned with the event's sales SHALL carry its id, event, SeatType name and price, its state, whether it is LowStock, and whether its resale is open, and the event's per-account limit SHALL be returned beside them. It SHALL NOT carry a TicketStock's quantity, sold count, or held count, nor the stocks of a sale's other events, so no fan learns how many tickets remain.

#### Scenario: Few left without a count

- **WHEN** ListByEvent returns a TicketStock of 150 that is Available and LowStock with 15 remaining
- **THEN** the response carries its state, LowStock, seat type and price, and no quantity, sold count or held count

#### Scenario: Sold out

- **WHEN** ListByEvent returns a TicketStock that sold out before its resale deadline
- **THEN** the response says it is SoldOut and its resale is open, and carries no count


## MODIFIED Requirements

### Requirement: Reading a sale needs no sign-in

ListByEvent SHALL accept a call with or without a sign-in, fail with InvalidArgument when the event is missing or malformed, and return TicketSaleUseCase.ListByEvent for the event.

#### Scenario: Guest opens the event page

- **WHEN** a caller who is not signed in calls ListByEvent for an event on sale
- **THEN** the event's sales are returned with the event's TicketStocks, each with its seat type and state

#### Scenario: Missing event

- **WHEN** ListByEvent is called without an event
- **THEN** it fails with InvalidArgument


## REMOVED Requirements

### Requirement: A returned sale never shows its counts

**Reason**: A sale now returns TicketStocks; buying listed tickets moves to the change resell-tickets-by-lottery, so whether resale is available is no longer returned.
**Migration**: See "A returned sale shows states, never counts".
