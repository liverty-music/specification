# components/usecase/ticket-sale/list-by-event Specification

## Purpose
TicketSaleUseCase.ListByEvent tells anyone looking at an event which sales offer its tickets, and for a first-come sale how its tickets stand.

## Requirements

### Requirement: The event's sales and their ticket types

ListByEvent SHALL take an event and the current time and read its sales with TicketSale.ListByEvent. It SHALL return each sale, ordered by start time, with only its TicketType for that event, a TicketType of a FirstCome sale with its state and whether it is LowStock at that time. It SHALL return an empty list when the event has no sale, and also when Event.IsEventPublished reports false for the event, as for a 中止 (cancelled) concert.

#### Scenario: On sale with few left
- **WHEN** an event whose first-come TicketType of 150 has 15 remaining is read at 12:00 inside the sale's window
- **THEN** the sale is returned with that TicketType OnSale and LowStock, with its price

#### Scenario: Last tickets in checkouts
- **WHEN** the first-come TicketType's remaining tickets are all held by others
- **THEN** it is returned AllHeld

#### Scenario: Tour presale seen from one date
- **WHEN** a sale offers TicketTypes for this event and two other events
- **THEN** the sale is returned with only the TicketType for this event

#### Scenario: Presale and general sale
- **WHEN** the event is offered by a presale starting 1 November and a general sale starting 20 November
- **THEN** both are returned, the presale first

#### Scenario: Concert cancelled
- **WHEN** the event's concert was cancelled
- **THEN** an empty list is returned

#### Scenario: Event without a sale
- **WHEN** the event has no TicketSale
- **THEN** an empty list is returned
