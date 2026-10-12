# components/adapter/fan/api/rpc/ticket-sale Specification

## Purpose
The fan-facing ticket sale service boundary: anyone, signed in or not, may read how an event's tickets are on sale.

## Requirements

### Requirement: Reading a sale needs no sign-in

ListByEvent SHALL accept a call with or without a sign-in, fail with InvalidArgument when the event is missing or malformed, and return TicketSaleUseCase.ListByEvent for the event.

#### Scenario: Guest opens the event page

- **WHEN** a caller who is not signed in calls ListByEvent for an event on sale
- **THEN** the event's sales are returned, each with its TicketType for the event and, for a first-come one, its state

#### Scenario: Missing event

- **WHEN** ListByEvent is called without an event
- **THEN** it fails with InvalidArgument

### Requirement: A returned sale never shows its counts

A TicketSale returned by the fan boundary SHALL carry its id, Series, name, method, start time, end time and verification requirement, and its one TicketType for the event with the TicketType's id, event, price, per-account limit and, for a FirstCome sale, its state and whether it is LowStock. It SHALL NOT carry a TicketType's quantity, sold count or held count, nor the TicketTypes of the sale's other events, so no fan learns how many tickets remain.

#### Scenario: Few left without a count

- **WHEN** ListByEvent returns a sale whose first-come TicketType of 150 is OnSale and LowStock with 15 remaining
- **THEN** the response carries its state, LowStock and price, and no quantity, sold count or held count
