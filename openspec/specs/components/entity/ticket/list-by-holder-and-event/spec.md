# components/entity/ticket/list-by-holder-and-event Specification

## Purpose
Lists the Tickets one account holds for one event.

## Requirements

### Requirement: Tickets of a holder for an event

ListByHolderAndEvent SHALL return every Ticket whose holder is the given account and whose event is the given event, Issued and Voided alike, in the order they were issued, and SHALL return an empty list when there are none.

#### Scenario: Group of tickets

- **WHEN** the account holds 3 Tickets for the event and 1 Ticket for another event
- **THEN** the 3 Tickets for the event are returned

#### Scenario: No tickets for the event

- **WHEN** the account holds no Ticket for the event
- **THEN** an empty list is returned
