# components/entity/ticket-stock/list-by-event Specification

## Purpose
Lists the TicketStocks of one event with their SeatTypes and, at a given time, their sold and held counts.

## Requirements

### Requirement: Stocks of an event

ListByEvent SHALL return every TicketStock of the given event, each with its SeatType and, at the given time, its sold count and held count, ordered by the SeatType's price, highest first, then by its name, and an empty list when the event has none or does not exist.

#### Scenario: Two seat types
- **WHEN** an event has an A席 stock at 7000 yen and an S席 stock at 9000 yen
- **THEN** the S席 stock is returned first, then the A席 stock

#### Scenario: Stock with holds
- **WHEN** the event's TicketStock has Checkouts holding 3 tickets at 18:00 and the list is read at 18:00
- **THEN** that TicketStock is returned with a held count of 3

#### Scenario: No stock
- **WHEN** the event has no TicketStock
- **THEN** an empty list is returned
