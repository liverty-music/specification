# RefundOrderUseCase.RefundOrder

## Purpose

RefundOrderUseCase.RefundOrder refunds one Paid Order for a stated reason — 中止 (cancellation), a 延期 (postponement) refund within its window, or a dispute — voiding its tickets, clawing back any payout already made, and marking the Order Refunded.

## Requirements

### Requirement: Reason and refundable order

RefundOrder SHALL take an Order, a reason — Cancellation, PostponementWindow or Dispute — and the current time. It SHALL fail with InvalidArgument when no reason is given. It SHALL read the Order with Order.Get, failing with NotFound when it does not exist. When the Order is already Refunded it SHALL return it unchanged and move no money. When the Order is not refundable it SHALL fail with FailedPrecondition.

#### Scenario: Reason missing

- **WHEN** RefundOrder is called without a reason
- **THEN** it fails with InvalidArgument and nothing changes

#### Scenario: Repeated refund

- **WHEN** RefundOrder is called for an Order that is already Refunded
- **THEN** the Order is returned unchanged and no refund or claw-back is made

#### Scenario: Unknown order

- **WHEN** the Order does not exist
- **THEN** RefundOrder fails with NotFound

### Requirement: Postponement refund window

For the reason PostponementWindow, RefundOrder SHALL read the reschedule time of the Order's event with Event.GetRescheduleTimeByOrder and SHALL fail with FailedPrecondition when the current time is more than 14 days after it. When the event has no reschedule time, the refund SHALL proceed.

#### Scenario: Within the window

- **WHEN** a postponement refund is requested 10 days after the event was rescheduled
- **THEN** the Order is refunded

#### Scenario: Window closed

- **WHEN** a postponement refund is requested 15 days after the event was rescheduled
- **THEN** RefundOrder fails with FailedPrecondition and nothing changes

#### Scenario: No reschedule time

- **WHEN** a postponement refund is requested for an event that has no reschedule time
- **THEN** the Order is refunded

### Requirement: Buyer refunded the full amount

For the reasons Cancellation and PostponementWindow, RefundOrder SHALL refund the Order's full amount to the buyer's original payment with Order.CreateRefund, against the charge recorded on the Order's Settlement or, when none is recorded, the charge found by Order.ResolveChargeRef. It SHALL fail with FailedPrecondition when the Order's payment service cannot issue refunds or the Order has no payment reference. For the reason Dispute it SHALL issue no refund, because the dispute has already returned the money to the cardholder.

#### Scenario: Cancellation refund

- **WHEN** an event is cancelled and a 16000 yen Order is refunded with the reason Cancellation
- **THEN** 16000 yen is refunded to the buyer's card

#### Scenario: Dispute

- **WHEN** RefundOrder runs with the reason Dispute
- **THEN** no refund is issued to the buyer and the rest of the refund still happens

### Requirement: Payout clawed back

When the Order's Settlement, read with Settlement.GetByOrderID, is Released, RefundOrder SHALL reverse every paid split that is not yet reversed with Settlement.ReverseTransfer for the split's amount. When it is Held, no payout is reversed and the Settlement becomes Reversed, so it is never paid out later. When the Order has no Settlement, nothing is clawed back. Only the paid splits are reversed: the platform fee was never paid out, so it is not recovered from the Organizer, and when a Released Order is refunded — in practice a Dispute that arrives after the release — the platform bears its fee.

#### Scenario: Payout already released

- **WHEN** the Order's Settlement is Released
- **THEN** each paid split is reversed and the Settlement becomes Reversed

#### Scenario: Payout not yet released

- **WHEN** the Order's Settlement is Held
- **THEN** no payout is reversed and the Settlement becomes Reversed

### Requirement: Refund recorded

After the money has moved, RefundOrder SHALL record the refund with Order.CommitRefund — the Order Refunded with its refund reference, all of its Tickets Voided, its Settlement Reversed — and return the Refunded Order. When Order.CommitRefund fails with FailedPrecondition because another refund of the same Order got there first, RefundOrder SHALL return the Order as read again with Order.Get. When a money movement fails, its error SHALL be returned and nothing is recorded; a retried RefundOrder refunds and reverses at most once.

#### Scenario: Tickets voided

- **WHEN** an Order with 2 Issued Tickets is refunded
- **THEN** the Order is Refunded and both Tickets are Voided

#### Scenario: Concurrent refund

- **WHEN** Order.CommitRefund fails with FailedPrecondition
- **THEN** RefundOrder returns the Order as it is now stored

#### Scenario: Retry after a failure

- **WHEN** a refund failed after the buyer was refunded and is run again
- **THEN** the buyer is not refunded a second time and the refund is recorded
