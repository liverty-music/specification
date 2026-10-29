# Spec Delta

## Purpose

Stores a new TicketStock: the tickets of one SeatType for one event of the SeatType's Series, with their quantity.

## ADDED Requirements

### Requirement: Store a ticket stock

Create SHALL store a TicketStock with the given event, SeatType and quantity and return it. It SHALL fail with InvalidArgument when the quantity breaks the TicketStock rules or the event is not of the SeatType's Series, with FailedPrecondition when the event or the SeatType does not exist, and with AlreadyExists when the event already has a TicketStock of the SeatType, storing nothing.

#### Scenario: Stock stored
- **WHEN** Create is called with 150 tickets of S席 for an event of S席's Series
- **THEN** the TicketStock is stored and returned

#### Scenario: Same seat type twice
- **WHEN** the event already has a TicketStock of S席
- **THEN** Create fails with AlreadyExists and stores nothing

#### Scenario: Event of another series
- **WHEN** the event is not of the SeatType's Series
- **THEN** Create fails with InvalidArgument and stores nothing

#### Scenario: Unknown event
- **WHEN** no event has the given id
- **THEN** Create fails with FailedPrecondition and stores nothing
