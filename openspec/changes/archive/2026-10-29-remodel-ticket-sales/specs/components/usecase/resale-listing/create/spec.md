# Spec Delta

## ADDED Requirements

### Requirement: List one of the fan's own tickets while its stock's resale is open

Create SHALL take the calling fan, a Ticket and the current time:
- It SHALL read the fan's Tickets with Ticket.ListByUser and fail with PermissionDenied, without revealing whether the Ticket exists, when the Ticket is not among them.
- It SHALL fail with FailedPrecondition when the Ticket is Voided or has an admit time.
- It SHALL read the Ticket's Order with Order.Get and the Order's TicketStock with TicketStock.Get. A Ticket bought first come and a Ticket won in a lottery are listed alike.
- It SHALL fail with FailedPrecondition when Event.IsEventPublished reports false for the Ticket's event, as for a 中止 (cancelled) concert.
- It SHALL read the event with Event.Get and fail with FailedPrecondition when the TicketStock's resale is not open at the current time with the event's resale deadline.
- It SHALL then call ResaleListing.Create with the Ticket, its Order, the fan, the TicketStock, its SeatType's price and the current time, return the listing, and return a failure of ResaleListing.Create unchanged.

#### Scenario: Fan lists a ticket after the stock sold out
- **WHEN** a fan holding 2 Issued S席 Tickets of a sold-out stock priced 5000 yen lists one of them the week before the event
- **THEN** a Listed listing for that Ticket with the price 5000 yen is returned

#### Scenario: Stock not sold out
- **WHEN** the fan lists a Ticket of a TicketStock that is not sold out
- **THEN** Create fails with FailedPrecondition and nothing is listed

#### Scenario: Admission has opened
- **WHEN** the fan lists a Ticket after the event's admission window opened
- **THEN** Create fails with FailedPrecondition and nothing is listed

#### Scenario: Ticket already used
- **WHEN** the fan lists a Ticket that was admitted
- **THEN** Create fails with FailedPrecondition

#### Scenario: Lottery ticket
- **WHEN** the fan lists a Ticket whose Order won a lottery entry, of a sold-out stock, before the resale deadline
- **THEN** a Listed listing for that Ticket is returned

#### Scenario: Concert cancelled
- **WHEN** the fan lists a Ticket of a cancelled concert
- **THEN** Create fails with FailedPrecondition

#### Scenario: Someone else's ticket
- **WHEN** the fan lists a Ticket of another User
- **THEN** Create fails with PermissionDenied and nothing is listed

#### Scenario: Listed twice
- **WHEN** the fan lists a Ticket that already has a Listed listing
- **THEN** Create fails with AlreadyExists

## REMOVED Requirements

### Requirement: List one of the fan's own tickets while resale is open

**Reason**: Resale belongs to the Ticket's TicketStock, read through its Order, instead of a TicketType.
**Migration**: See "List one of the fan's own tickets while its stock's resale is open".
