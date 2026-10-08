# Spec Delta

## Purpose

The fan-facing ticket sale service boundary: anyone, signed in or not, may read how an event's tickets are on sale.

## ADDED Requirements

### Requirement: Reading a sale needs no sign-in

Get SHALL accept a call with or without a sign-in, fail with InvalidArgument when the event is missing or malformed, and return TicketSaleUseCase.Get for the event.

#### Scenario: Guest opens the event page

- **WHEN** a caller who is not signed in calls Get for an event on sale
- **THEN** the sale and its state are returned

#### Scenario: Missing event

- **WHEN** Get is called without an event
- **THEN** it fails with InvalidArgument
