# components/entity/order/list-by-event Specification

## Purpose
Order.ListByEvent returns every Order whose Tickets admit to one Event, in any status, so an admin can see and refund the purchases of that Event.

## Requirements

### Requirement: ListByEvent returns the Event's Orders

ListByEvent SHALL return every Order whose source, a LotteryEntry or a Checkout, is for a TicketType of the given Event, whatever the Order's status, oldest pay time first. An Order created by an official resale purchase is one of these Orders. It SHALL return an empty list when the Event has no Order or no Event has the id, and SHALL fail with InvalidArgument when no Event is given.

#### Scenario: Paid, refunded and resale orders
- **WHEN** the Event has one Paid Order from a Checkout, one Refunded Order from a won LotteryEntry and one Paid Order from an official resale purchase
- **THEN** all three are returned, oldest pay time first

#### Scenario: Orders of another event
- **WHEN** another Event of the same Series has an Order and this Event has none
- **THEN** an empty list is returned

#### Scenario: No event given
- **WHEN** ListByEvent is called with no Event
- **THEN** it fails with InvalidArgument
