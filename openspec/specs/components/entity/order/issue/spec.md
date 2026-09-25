# Order.Issue

## Purpose

Stores a new Order together with the Tickets it issues.

## Requirements

### Requirement: Order, tickets and settlement together, once per application

Issue SHALL store the Order, all of its Tickets, and a Held Settlement for the Order's event and Organizer — with one split paying that Organizer its net share of the Order's amount, after deducting the platform fee (a flat 5% of the Order's amount, rounded down) — together or not at all, and SHALL fail with AlreadyExists when an Order already exists for the same application.

#### Scenario: Order issued

- **WHEN** Issue is called with an Order, its 3 Tickets, and a Settlement for the event's Organizer
- **THEN** the Order, the 3 Tickets, and a Held Settlement with one Organizer split are stored

#### Scenario: Failure stores nothing

- **WHEN** storing any Ticket or the Settlement fails
- **THEN** neither the Order, any Ticket, nor the Settlement is stored

#### Scenario: Second order for the application

- **WHEN** an Order already exists for the application
- **THEN** Issue fails with AlreadyExists and stores nothing
