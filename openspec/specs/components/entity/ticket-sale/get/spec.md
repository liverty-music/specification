# components/entity/ticket-sale/get Specification

## Purpose
Reads one TicketSale by its id with its TicketTypes, each first-come type with its held count at a given time.

## Requirements

### Requirement: Get returns the sale and its events

Get SHALL return the TicketSale with the given id with the events it names, and SHALL fail with NotFound when no TicketSale has the id.

#### Scenario: Sale covering several events

- **WHEN** Get is called with the id of a sale that names two events
- **THEN** that sale is returned with both events

#### Scenario: Unknown sale

- **WHEN** no TicketSale has the id
- **THEN** Get fails with NotFound
