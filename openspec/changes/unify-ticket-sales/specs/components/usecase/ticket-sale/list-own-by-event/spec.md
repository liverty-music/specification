# Spec Delta

## Purpose

TicketSaleUseCase.ListOwnByEvent shows an Organizer every sale of one of its events, with the entry stats of each lottery TicketType, the sold and held counts of each first-come TicketType, and whether each lottery sale has been drawn.

## ADDED Requirements

### Requirement: The owner sees the event's sales with their entry stats

ListOwnByEvent SHALL take the caller's Organizer, an event and the current time. It SHALL fail with PermissionDenied, without revealing whether the event exists, when Event.GetOrganizerID fails with NotFound or returns another Organizer. It SHALL list the event's sales with TicketSale.ListByEvent and return each sale with its TicketTypes, adding for each TicketType of a Lottery sale the entry stats from LotteryEntry.GetStatsByTicketType, and for each TicketType of a FirstCome sale its quantity, sold count, and held count and state at that time. It SHALL return an empty list when the event has no sale.

#### Scenario: Drawn presale and upcoming general sale
- **WHEN** the owner reads an event with a drawn presale and a general sale that has not opened
- **THEN** both sales are returned in start order, the presale drawn with its entry, ticket, winner and loser counts

#### Scenario: Owner checks first-come sales
- **WHEN** the owner reads an event whose first-come TicketType of 150 has 100 sold and 6 held
- **THEN** the sale is returned with that TicketType's quantity 150, 100 sold and 6 held

#### Scenario: Event without a sale
- **WHEN** the owner reads an event that no sale offers
- **THEN** an empty list is returned

#### Scenario: Another organizer's event
- **WHEN** an operator reads the sales of another Organizer's event
- **THEN** ListOwnByEvent fails with PermissionDenied
