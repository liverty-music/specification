# Spec Delta

## Purpose

Stores a new TicketSale for an event, one per event.

## ADDED Requirements

### Requirement: One sale per event

Create SHALL store a new TicketSale with a sold count of 0 and return it. It SHALL fail with InvalidArgument when the sale breaks the TicketSale rules, and with AlreadyExists when the event already has a TicketSale.

#### Scenario: First sale for an event

- **WHEN** a valid sale is created for an event without one
- **THEN** it is stored with a sold count of 0

#### Scenario: Second sale for the event

- **WHEN** the event already has a TicketSale
- **THEN** Create fails with AlreadyExists and stores nothing
