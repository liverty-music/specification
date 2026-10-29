# components/usecase/ticket-stock/list-by-event Specification

## Purpose
TicketStockUseCase.ListByEvent shows an Organizer the ticket stocks of one of its events with their seat types and how many tickets are sold and held.

## Requirements

### Requirement: A member of the owning Organizer lists an event's stocks

ListByEvent SHALL take the caller's Organizer, an event and the current time. It SHALL fail with PermissionDenied, without revealing whether the event exists, when Event.GetOrganizerID fails with NotFound or returns another Organizer. It SHALL return the event's TicketStocks from TicketStock.ListByEvent, each with its SeatType, its quantity, and its sold count, held count and state at that time, and an empty list when the event has none.

#### Scenario: Stocked event
- **WHEN** a member lists an event with an S席 stock of 150 that has 100 sold and 6 held
- **THEN** the S席 stock is returned with its quantity 150, 100 sold and 6 held

#### Scenario: Not stocked yet
- **WHEN** a member lists an event without a TicketStock
- **THEN** an empty list is returned

#### Scenario: Another Organizer's event
- **WHEN** a member lists the stocks of another Organizer's event
- **THEN** ListByEvent fails with PermissionDenied
