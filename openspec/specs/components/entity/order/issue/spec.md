# Order.Issue

## Purpose

Stores a new Order together with the Tickets it issues.

## Requirements

### Requirement: Order, tickets and settlement together, once per source

Issue SHALL store, together or not at all:
- the Order;
- all of its Tickets;
- a Held Settlement for the Order's event and Organizer, with one split paying that Organizer its net share of the Order's amount after the platform fee at the Organizer's platform fee rate;
- when the Order's source is a Reservation, that Reservation made Completed.

It SHALL fail with AlreadyExists when an Order already exists for the same source. When the source is a Reservation, it SHALL fail with FailedPrecondition, storing nothing, unless that Reservation is Committed and has a capture time.

#### Scenario: Order issued

- **WHEN** Issue is called with an Order, its 3 Tickets, and a Settlement for the event's Organizer
- **THEN** the Order, the 3 Tickets and a Held Settlement with one Organizer split are stored

#### Scenario: Order issued from a checkout

- **WHEN** Issue is called with an Order whose source is a Committed, charged Reservation
- **THEN** the Order and its Tickets are stored and the Reservation is Completed

#### Scenario: Reservation not charged

- **WHEN** the source Reservation is Committed but has no capture time
- **THEN** Issue fails with FailedPrecondition and stores nothing

#### Scenario: Failure stores nothing

- **WHEN** storing any Ticket or the Settlement fails
- **THEN** neither the Order, any Ticket nor the Settlement is stored, and a Reservation stays Committed

#### Scenario: Second order for the application

- **WHEN** an Order already exists for the application
- **THEN** Issue fails with AlreadyExists and stores nothing

#### Scenario: Second order for the reservation

- **WHEN** an Order already exists for the Reservation
- **THEN** Issue fails with AlreadyExists and stores nothing
