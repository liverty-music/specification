# Spec Delta

## Purpose

TicketSaleUseCase.GetOwn shows an Organizer the sale of one of its events, including how many tickets are offered and sold.

## ADDED Requirements

### Requirement: The owner sees its sale with the counts

GetOwn SHALL take the caller's Organizer, an event and the current time. It SHALL fail with PermissionDenied, without revealing whether the event exists, when Event.GetOrganizerID fails with NotFound or returns another Organizer. It SHALL read the sale with TicketSale.GetByEvent, failing with NotFound when the event has none, and return the sale with its quantity, sold count, and held count and state at that time.

#### Scenario: Owner checks sales

- **WHEN** the owner reads a sale of 150 with 100 sold and 6 held
- **THEN** the sale is returned with quantity 150, 100 sold and 6 held

#### Scenario: Another organizer's event

- **WHEN** an operator reads the sale of another Organizer's event
- **THEN** GetOwn fails with PermissionDenied
