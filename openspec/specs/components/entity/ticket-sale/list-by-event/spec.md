# components/entity/ticket-sale/list-by-event Specification

## Purpose
Lists the TicketSales that offer a TicketType for one event, with the stock of each first-come TicketType at a given time.

## Requirements

### Requirement: Sales of an event

ListByEvent SHALL return every sale that has a TicketType for the given event, each with all of its TicketTypes and, for each TicketType of a FirstCome sale, its held count at the given time, ordered by start time, and SHALL return an empty list when the event has none.

#### Scenario: Presale and general sale
- **WHEN** the event is offered by a sale starting 1 November and a sale starting 20 November
- **THEN** both sales are returned, the 1 November sale first

#### Scenario: Sale covering several events
- **WHEN** a sale offers TicketTypes for this event and two other events
- **THEN** the sale is returned once, with all three TicketTypes

#### Scenario: First-come sale with holds
- **WHEN** the event's FirstCome TicketType has Checkouts holding 3 tickets at 18:00 and the list is read at 18:00
- **THEN** the sale is returned with that TicketType's held count of 3

#### Scenario: No sale
- **WHEN** no sale offers the event
- **THEN** an empty list is returned
