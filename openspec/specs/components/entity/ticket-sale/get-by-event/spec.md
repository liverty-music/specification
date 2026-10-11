# components/entity/ticket-sale/get-by-event Specification

## Purpose
Reads the TicketSale of an event, if it has one, with its held count at a given time.

## Requirements

### Requirement: The event's sale

GetByEvent SHALL return the event's TicketSale, with its held count at the given time, and SHALL fail with NotFound when the event has none.

#### Scenario: Event on sale

- **WHEN** the event has a TicketSale
- **THEN** that sale is returned with its held count

#### Scenario: Event without a sale

- **WHEN** the event has no TicketSale
- **THEN** GetByEvent fails with NotFound
