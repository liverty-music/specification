# Spec Delta

## Purpose

TicketSaleUseCase.Configure lets an Organizer put one of its published events on sale first come, first served, or change that sale.

## ADDED Requirements

### Requirement: Only the owner of a published, timed event with seller details

Configure SHALL take the caller's Organizer, an event, a sale start, a sale end, a price, a quantity and an optional per-account limit, and the current time:
- It SHALL fail with PermissionDenied, without revealing whether the event exists, when Event.GetOrganizerID fails with NotFound or returns another Organizer.
- It SHALL fail with FailedPrecondition when Event.IsEventPublished reports false.
- It SHALL fail with FailedPrecondition when Event.GetEventStartTime returns no start time.
- It SHALL fail with FailedPrecondition when the Organizer, read with Organizer.Get, has no complete seller details.
- It SHALL fail with InvalidArgument when the sale end is after the event's start time.

#### Scenario: Another organizer's event

- **WHEN** an operator configures a sale for an event owned by another Organizer
- **THEN** Configure fails with PermissionDenied and nothing is stored

#### Scenario: Start time not announced

- **WHEN** the event has no start time
- **THEN** Configure fails with FailedPrecondition

#### Scenario: Seller details missing

- **WHEN** the Organizer has no address in its seller details
- **THEN** Configure fails with FailedPrecondition and nothing is stored

#### Scenario: Sale ends after the show starts

- **WHEN** the event starts at 19:00 and the sale end is 19:30 the same day
- **THEN** Configure fails with InvalidArgument

### Requirement: Create the sale, or update it

When no sale end is given, Configure SHALL use the event's start time, whether it creates or changes the sale. When the event has no TicketSale, read with TicketSale.GetByEvent, Configure SHALL create one with TicketSale.Create. Otherwise it SHALL change it with TicketSale.Update, whose rules on the price and the quantity apply. Configure SHALL return the sale.

#### Scenario: First configuration

- **WHEN** the owner configures a sale of 150 tickets at 3000 yen for an event starting at 19:00 without a sale end
- **THEN** a TicketSale ending at 19:00 with a per-account limit of 4 is created and returned

#### Scenario: More tickets later

- **WHEN** the owner raises the quantity of the event's sale from 150 to 180
- **THEN** the sale's quantity is 180
