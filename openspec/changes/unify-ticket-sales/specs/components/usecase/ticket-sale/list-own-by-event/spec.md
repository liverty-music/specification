# Spec Delta

## Purpose

TicketSaleUseCase.ListOwnByEvent shows an Organizer every sale of one of its events, with the tallies of each lottery TicketType and whether each sale has been drawn.

## ADDED Requirements

### Requirement: The owner sees the event's sales with their tallies

ListOwnByEvent SHALL take the caller's Organizer and an event. It SHALL fail with PermissionDenied, without revealing whether the event exists, when Event.GetOrganizerID fails with NotFound or returns another Organizer. It SHALL list the event's sales with TicketSale.ListByEvent and return each sale with its TicketTypes, adding for each TicketType of a Lottery sale the tallies from LotteryEntry.GetTicketTypeStats. It SHALL return an empty list when the event has no sale.

#### Scenario: Drawn presale and upcoming general sale
- **WHEN** the owner reads an event with a drawn presale and a general sale that has not opened
- **THEN** both sales are returned in start order, the presale drawn with its entry, ticket, winner and waitlist counts

#### Scenario: Event without a sale
- **WHEN** the owner reads an event that no sale offers
- **THEN** an empty list is returned

#### Scenario: Another organizer's event
- **WHEN** an operator reads the sales of another Organizer's event
- **THEN** ListOwnByEvent fails with PermissionDenied
