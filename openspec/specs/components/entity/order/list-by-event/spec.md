# components/entity/order/list-by-event Specification

## Purpose
Order.ListByEvent returns the Paid and Refunded Orders of one Event, so an admin can see and refund the purchases of that Event.

## Requirements

### Requirement: ListByEvent returns the Event's paid and refunded orders

ListByEvent SHALL return every Paid or Refunded Order whose TicketStock is of the given Event, oldest pay time first. Pending and Void Orders SHALL NOT be returned. It SHALL return an empty list when the Event has no such Order or no Event has the id, and SHALL fail with InvalidArgument when no Event is given.

#### Scenario: Paid and refunded orders
- **WHEN** the Event has one Paid Order from a Checkout and one Refunded Order from a won LotteryEntry
- **THEN** both are returned, oldest pay time first

#### Scenario: Pending and void orders
- **WHEN** the Event has one Pending Order of an Entered LotteryEntry and one Void Order of an expired Checkout
- **THEN** neither is returned

#### Scenario: Orders of another event
- **WHEN** another Event of the same Series has an Order and this Event has none
- **THEN** an empty list is returned

#### Scenario: No event given
- **WHEN** ListByEvent is called with no Event
- **THEN** it fails with InvalidArgument
