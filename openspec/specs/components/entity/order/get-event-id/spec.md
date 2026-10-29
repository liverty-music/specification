# components/entity/order/get-event-id Specification

## Purpose
Order.GetEventID returns the id of the Event an Order is for, the Event of its TicketStock, so a refund can check that Event's state.

## Requirements

### Requirement: The Event of an Order

GetEventID SHALL return the id of the Event of the Order's TicketStock. It SHALL fail with NotFound when no Order has the id.

#### Scenario: Order from a checkout
- **WHEN** the Order was bought through a Checkout for a TicketStock of Event E
- **THEN** GetEventID returns E

#### Scenario: Order from a won lottery entry
- **WHEN** the Order was entered through a LotteryEntry for a TicketStock of Event E
- **THEN** GetEventID returns E

#### Scenario: Unknown order
- **WHEN** no Order has the id
- **THEN** GetEventID fails with NotFound
