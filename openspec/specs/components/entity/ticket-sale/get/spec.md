# components/entity/ticket-sale/get Specification

## Purpose
Reads one TicketSale by its id with its TicketTypes, each first-come type with its held count at a given time.

## Requirements

### Requirement: Get returns the sale and its held count

Get SHALL return the TicketSale with the given id with all of its TicketTypes, each TicketType of a FirstCome sale with its held count at the given time, and SHALL fail with NotFound when no TicketSale has the id.

#### Scenario: Sale with holds

- **WHEN** a FirstCome sale whose TicketType's Checkouts hold 3 tickets at 18:00 is read at 18:00
- **THEN** the sale is returned with its TicketType and 3 held tickets

#### Scenario: Sale covering several events

- **WHEN** Get is called with the id of a sale with TicketTypes for two events
- **THEN** that sale is returned with both TicketTypes

#### Scenario: Unknown sale

- **WHEN** no TicketSale has the id
- **THEN** Get fails with NotFound
