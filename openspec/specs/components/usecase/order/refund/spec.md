# OrderUseCase.Refund

## Purpose

OrderUseCase.Refund refunds one Paid Order for a stated reason — 中止 (cancellation) or a dispute — voiding its tickets, clawing back any payout already made, and marking the Order Refunded.

## Requirements

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

### Requirement: Fan refunded the full amount

For the reason Cancellation, Refund SHALL refund the price of the Order's Tickets that are still Issued — the Order's amount divided by its number of Tickets, times the number still Issued — to the fan's original payment with Order.CreateRefund for the Order's own refund, against the charge recorded on the Order's Settlement or, when none is recorded, the charge found by Order.GetProviderChargeID. Tickets the fan resold through official resale were already refunded less the resale fee and are not refunded again. When no Ticket of the Order is Issued, it SHALL issue no refund. It SHALL fail with FailedPrecondition when the Order's payment provider cannot issue refunds or the Order has no provider payment ID. For the reason Dispute it SHALL issue no refund, because the dispute has already returned the money to the fan.

#### Scenario: Cancellation refund

- **WHEN** an event is cancelled and a 16000 yen Order is refunded with the reason Cancellation
- **THEN** 16000 yen is refunded to the fan's card

#### Scenario: Cancellation after a resale

- **WHEN** an event is cancelled and a 10000 yen Order for 2 tickets, one of which was resold, is refunded with the reason Cancellation
- **THEN** 5000 yen is refunded to the fan's card

#### Scenario: Every ticket resold

- **WHEN** an event is cancelled and every Ticket of the Order was resold
- **THEN** no refund is issued and the Order is recorded Refunded

#### Scenario: Dispute

- **WHEN** Refund runs with the reason Dispute
- **THEN** no refund is issued to the fan and the rest of the refund still happens

### Requirement: Payout clawed back

When the Order's Settlement, read with Settlement.GetByOrderID, is Released, Refund SHALL reverse every paid split that is not yet reversed with Settlement.ReversePayout for the split's amount. When it is Held, no payout is reversed and the Settlement becomes Reversed, so it is never paid out later. When it is already Reversed, as after every Ticket of the Order was resold, nothing is clawed back and no Settlement is given to Order.CommitRefund. When the Order has no Settlement, nothing is clawed back. Only the paid splits are reversed: the platform fee was never paid out, so it is not recovered from the Organizer, and when a Released Order is refunded — in practice a Dispute that arrives after the release — the platform bears its fee.

#### Scenario: Payout already released

- **WHEN** the Order's Settlement is Released
- **THEN** each paid split is reversed and the Settlement becomes Reversed

#### Scenario: Payout not yet released

- **WHEN** the Order's Settlement is Held
- **THEN** no payout is reversed and the Settlement becomes Reversed

#### Scenario: Settlement given up by resales

- **WHEN** the Order's Settlement was Reversed because every Ticket was resold
- **THEN** nothing is clawed back and the Order is recorded Refunded

### Requirement: Refund recorded

After the money has moved, Refund SHALL record the refund with Order.CommitRefund — the Order Refunded with its provider refund ID, all of its Tickets Voided, its Settlement Reversed — and return the Refunded Order. When Order.CommitRefund fails with FailedPrecondition because another refund of the same Order got there first, Refund SHALL return the Order as read again with Order.Get. When a money movement fails, its error SHALL be returned and nothing is recorded; a retried Refund refunds and reverses at most once.

#### Scenario: Tickets voided

- **WHEN** an Order with 2 Issued Tickets is refunded
- **THEN** the Order is Refunded and both Tickets are Voided

#### Scenario: Concurrent refund

- **WHEN** Order.CommitRefund fails with FailedPrecondition
- **THEN** Refund returns the Order as it is now stored

#### Scenario: Retry after a failure

- **WHEN** a refund failed after the fan was refunded and is run again
- **THEN** the fan is not refunded a second time and the refund is recorded
