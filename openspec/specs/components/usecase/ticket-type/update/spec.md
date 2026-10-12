# components/usecase/ticket-type/update Specification

## Purpose
TicketTypeUseCase.Update lets an Organizer change the price, quantity and per-account limit that one of its TicketSales offers for an event: for a lottery sale until its window opens, for a first-come sale under the price lock and the sold-plus-held floor.

## Requirements

### Requirement: Only the Series' Organizer changes a ticket type

Update SHALL take the caller's Organizer, a TicketType, a price, a quantity, a per-account limit and the current time. It SHALL read the TicketType and its sale with TicketType.Get, failing with NotFound when it does not exist, read the sale's Series with Series.GetAuthored, and fail with PermissionDenied when the calling Organizer does not own that Series.

#### Scenario: Another Organizer's ticket type
- **WHEN** an Organizer changes a TicketType of a sale on a Series owned by a different Organizer
- **THEN** Update fails with PermissionDenied and nothing changes

#### Scenario: Unknown ticket type
- **WHEN** the TicketType does not exist
- **THEN** Update fails with NotFound

### Requirement: A lottery ticket type changes only before its sale opens

Update SHALL fail with FailedPrecondition, changing nothing, when the sale's method is Lottery and the current time is at or after the sale's start time, so every entry is made against the price and quantity that are drawn.

#### Scenario: Lottery ticket type before the sale opens
- **WHEN** the TicketType of a Lottery sale opening on 1 November is changed on 25 October from 100 to 120 tickets
- **THEN** its quantity is 120

#### Scenario: Lottery sale already open
- **WHEN** the TicketType of a Lottery sale that opened on 1 November is changed on 3 November
- **THEN** Update fails with FailedPrecondition and nothing changes

### Requirement: Store the change

Update SHALL store the price, quantity and per-account limit with TicketType.Update, whose rules apply, among them for a first-come TicketType the price lock while tickets are held or sold and the floor of the sold count plus the tickets held, and return the updated TicketType. Errors from TicketType.Update SHALL be returned unchanged.

#### Scenario: More tickets later
- **WHEN** the owner raises the quantity of an on-sale first-come TicketType from 150 to 180
- **THEN** the TicketType's quantity is 180

#### Scenario: Price while tickets are held
- **WHEN** the owner changes the price of a first-come TicketType while a fan's Checkout holds 2 tickets
- **THEN** Update fails with FailedPrecondition and nothing changes
