# components/entity/order/get-event-id Specification

## Purpose
Order.GetEventID returns the id of the Event an Order is for, the Event of the TicketType its source was for, so a refund can check that Event's state.

## Requirements

### Requirement: The Event of an Order

GetEventID SHALL return the id of the Event of the TicketType that the Order's source, a LotteryEntry or a Checkout, was for. It SHALL fail with NotFound when no Order has the id.

#### Scenario: Order from a checkout
- **WHEN** the Order was created from a Checkout for a TicketType of Event E
- **THEN** GetEventID returns E

#### Scenario: Order from a won lottery entry
- **WHEN** the Order was created from a won LotteryEntry for a TicketType of Event E
- **THEN** GetEventID returns E

#### Scenario: Unknown order
- **WHEN** no Order has the id
- **THEN** GetEventID fails with NotFound
