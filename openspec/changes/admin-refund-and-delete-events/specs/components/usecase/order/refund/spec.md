## MODIFIED Requirements

### Requirement: Reason and refundable order

Refund SHALL take an Order, a reason — Cancellation or Dispute — and the current time. It SHALL fail with InvalidArgument when no reason is given. It SHALL read the Order with Order.Get, failing with NotFound when it does not exist. When the Order is already Refunded it SHALL return it unchanged and move no money. When the Order is not refundable it SHALL fail with FailedPrecondition. For the reason Cancellation it SHALL read the Order's Event with Order.GetEventID and Event.Get, and fail with FailedPrecondition, moving no money, when that Event is not CANCELLED; a 中止 (cancellation) refund is only for a cancelled Event. The reason Dispute SHALL be accepted whatever the Event's state.

#### Scenario: Reason missing

- **WHEN** Refund is called without a reason
- **THEN** it fails with InvalidArgument and nothing changes

#### Scenario: Repeated refund

- **WHEN** Refund is called for an Order that is already Refunded
- **THEN** the Order is returned unchanged and no refund or claw-back is made

#### Scenario: Unknown order

- **WHEN** the Order does not exist
- **THEN** Refund fails with NotFound

#### Scenario: Cancellation refund for an event still on sale

- **WHEN** Refund is called with the reason Cancellation for a Paid Order whose Event is PUBLISHED
- **THEN** it fails with FailedPrecondition, no money moves and the Order stays Paid

#### Scenario: Cancellation refund for a cancelled event

- **WHEN** Refund is called with the reason Cancellation for a Paid Order whose Event is CANCELLED
- **THEN** the Order is refunded

#### Scenario: Dispute for an event still on sale

- **WHEN** Refund is called with the reason Dispute for a Paid Order whose Event is PUBLISHED
- **THEN** the Order is refunded without a check of the Event's state
