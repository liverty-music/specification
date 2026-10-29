# components/usecase/ticket-sale/list-by-event Specification

## Purpose
TicketSaleUseCase.ListByEvent tells anyone looking at an event which sales offer its tickets, and for a first-come sale how its tickets stand.

## Requirements

### Requirement: The event's sales and its ticket stocks

ListByEvent SHALL take an event and the current time and read its sales with TicketSale.ListByEvent and its TicketStocks with TicketStock.ListByEvent. It SHALL return the sales ordered by start time, and once for the event, shared by every sale, each TicketStock with its SeatType's name and price, its state, whether it is LowStock, and whether its resale is open at that time, with the resale deadline read from the event with Event.Get, and the event's per-account limit. It SHALL return no sale and no TicketStock when the event has no sale, and also when Event.IsEventPublished reports false for the event, as for a 中止 (cancelled) concert.

#### Scenario: Available with few left
- **WHEN** an event whose S席 TicketStock of 150 has 15 remaining is read at 12:00 inside a FirstCome sale's window
- **THEN** the sale is returned with the S席 stock Available and LowStock, with its price

#### Scenario: Last tickets in checkouts
- **WHEN** a TicketStock's remaining tickets are all held by others
- **THEN** it is returned AllHeld

#### Scenario: Sold out before the resale deadline
- **WHEN** a TicketStock sold out and the resale deadline has not passed
- **THEN** it is returned SoldOut with resale open

#### Scenario: Tour presale seen from one date
- **WHEN** a sale names this event and two other events
- **THEN** the sale is returned with only this event's TicketStocks

#### Scenario: Presale and general sale
- **WHEN** the event is named by a presale starting 1 November and a general sale starting 20 November
- **THEN** both are returned, the presale first, with the same TicketStocks

#### Scenario: Concert cancelled
- **WHEN** the event's concert was cancelled
- **THEN** no sale and no TicketStock are returned

#### Scenario: Event without a sale
- **WHEN** no TicketSale names the event
- **THEN** no sale and no TicketStock are returned
