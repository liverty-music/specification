# components/entity/ticket-sale/set-window Specification

## Purpose
Replaces the start and end times of one TicketSale and returns the updated sale with its TicketTypes.

## Requirements

### Requirement: Set the window

SetWindow SHALL store the given start and end times for the TicketSale, leave its other attributes and its TicketTypes unchanged and return the updated sale with its TicketTypes. It SHALL fail with InvalidArgument when the window breaks the TicketSale rules, and with NotFound when no TicketSale has the id.

#### Scenario: Window moved
- **WHEN** a sale running from 1 to 10 November is set to run from 2 to 11 November
- **THEN** the returned sale runs from 2 to 11 November and its TicketTypes are unchanged

#### Scenario: Lottery window too long
- **WHEN** a Lottery sale's window is set to 15 days
- **THEN** SetWindow fails with InvalidArgument and nothing changes

#### Scenario: Unknown sale
- **WHEN** no TicketSale has the id
- **THEN** SetWindow fails with NotFound
