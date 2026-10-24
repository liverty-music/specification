## Purpose

OrderUseCase.ListByEvent gives an admin every Order of one Event, in any status, so the admin console can show and refund the purchases of a cancelled Event.

## ADDED Requirements

### Requirement: An Event's orders for admins

ListByEvent SHALL take an Event and return the result of Order.ListByEvent for it unchanged. An Event with no Order, and an Event that does not exist, SHALL yield an empty list, not an error.

#### Scenario: Cancelled event with refunded and paid orders
- **WHEN** a CANCELLED Event has one Paid and one Refunded Order
- **THEN** both are returned

#### Scenario: Unknown event
- **WHEN** no Event has the id
- **THEN** an empty list is returned
