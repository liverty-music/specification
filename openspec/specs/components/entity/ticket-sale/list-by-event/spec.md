# components/entity/ticket-sale/list-by-event Specification

## Purpose
Lists the TicketSales that name one event, each with that event's TicketStocks and their sold and held counts at a given time.

## Requirements

### Requirement: Sales naming an event

ListByEvent SHALL return every sale that names the given event, each with the events it names and with the given event's TicketStocks, each TicketStock with its SeatType and, at the given time, its sold count and held count, ordered by start time, and SHALL return an empty list when no sale names the event.

#### Scenario: Presale and general sale
- **WHEN** the event is named by a sale starting 1 November and a sale starting 20 November
- **THEN** both sales are returned, the 1 November sale first

#### Scenario: Sale covering several events
- **WHEN** a sale names this event and two other events
- **THEN** the sale is returned once, naming all three events, with this event's TicketStocks only

#### Scenario: First-come sale with holds
- **WHEN** the event's S席 TicketStock has Checkouts holding 3 tickets at 18:00 and the list is read at 18:00
- **THEN** each sale is returned with that TicketStock's held count of 3

#### Scenario: Sold-out stock
- **WHEN** the event's TicketStock of 150 has sold 150
- **THEN** each sale is returned with that TicketStock's sold count of 150

#### Scenario: No sale
- **WHEN** no sale names the event
- **THEN** an empty list is returned
