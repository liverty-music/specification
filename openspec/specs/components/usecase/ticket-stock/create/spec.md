# components/usecase/ticket-stock/create Specification

## Purpose
TicketStockUseCase.Create lets an Organizer stock one of its events with tickets of one of its Series' seat types, with the quantity for that event's venue.

## Requirements

### Requirement: Only the owner stocks an event with its own seat type

Create SHALL take the caller's Organizer, an event, a SeatType and a quantity. It SHALL read the event with Event.Get and its Series with Series.GetAuthored, and fail with PermissionDenied, without revealing whether it exists, when the event does not exist or its Series is owned by another Organizer. It SHALL fail with InvalidArgument when the SeatType is not among the Series' SeatTypes from SeatType.ListBySeries, or when the quantity breaks the TicketStock rules. It SHALL fail with FailedPrecondition when the event is CANCELLED. It SHALL then store the stock with TicketStock.Create and return it; TicketStock.Create fails with AlreadyExists when the event already has a TicketStock of that SeatType, and its failures are returned unchanged.

#### Scenario: Two days at one venue
- **WHEN** the owner stocks both events of a 2-day run with 150 S席 tickets each, from the Series' one S席
- **THEN** two TicketStocks are stored, one per event, both of the same SeatType

#### Scenario: Seat type of another series
- **WHEN** the SeatType belongs to another Series
- **THEN** Create fails with InvalidArgument and nothing is stored

#### Scenario: Same seat type twice
- **WHEN** the event already has an S席 TicketStock and the owner stocks it with S席 again
- **THEN** Create fails with AlreadyExists and nothing is stored

#### Scenario: Cancelled event
- **WHEN** the event is CANCELLED
- **THEN** Create fails with FailedPrecondition and nothing is stored

#### Scenario: Another Organizer's event
- **WHEN** a member stocks an event of a Series owned by another Organizer
- **THEN** Create fails with PermissionDenied and nothing is stored
