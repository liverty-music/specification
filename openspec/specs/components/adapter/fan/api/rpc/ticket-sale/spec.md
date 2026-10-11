# components/adapter/fan/api/rpc/ticket-sale Specification

## Purpose
The fan-facing ticket sale service boundary: anyone, signed in or not, may read how an event's tickets are on sale.

## Requirements

### Requirement: Reading a sale needs no sign-in

Get SHALL accept a call with or without a sign-in, fail with InvalidArgument when the event is missing or malformed, and return TicketSaleUseCase.Get for the event.

#### Scenario: Guest opens the event page

- **WHEN** a caller who is not signed in calls Get for an event on sale
- **THEN** the sale and its state are returned

#### Scenario: Missing event

- **WHEN** Get is called without an event
- **THEN** it fails with InvalidArgument

### Requirement: A returned sale never shows its counts

A TicketSale returned by the fan boundary SHALL carry its id, event, method, sale start, sale end, price, per-account limit, state and whether it is LowStock, and SHALL NOT carry its quantity, sold count or held count, so no fan learns how many tickets remain.

#### Scenario: Few left without a count

- **WHEN** Get returns an OnSale, LowStock sale of 150 with 15 remaining
- **THEN** the response carries its state, LowStock and price, and no quantity, sold count or held count
