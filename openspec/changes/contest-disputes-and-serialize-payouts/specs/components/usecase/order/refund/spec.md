# Spec Delta

## MODIFIED Requirements

### Requirement: Reason and refundable order

Refund SHALL take an Order and the reason Cancellation, and SHALL act at the current time. It SHALL fail with InvalidArgument when no reason is given or the reason is Dispute; a dispute is settled by its outcome (DisputeUseCase.Settle), not by a refund. It SHALL read the Order with Order.Get, failing with NotFound when it does not exist. When the Order is already Refunded it SHALL return it unchanged and move no money. When the Order is not refundable it SHALL fail with FailedPrecondition. It SHALL read the Order's Disputes with Dispute.ListByOrder and fail with FailedPrecondition, moving no money, while the Order is disputed (an open or unsettled Dispute, Dispute "Unsettled outcome"): the dispute's answer and outcome decide the money. It SHALL read the Order's Event with Order.GetEventID and Event.Get, and fail with FailedPrecondition, moving no money, when that Event is not CANCELLED; a 中止 (cancellation) refund is only for a cancelled Event.

#### Scenario: Reason missing

- **WHEN** Refund is called without a reason
- **THEN** it fails with InvalidArgument and nothing changes

#### Scenario: Dispute for an event still on sale

- **WHEN** Refund is called with the reason Dispute for a Paid Order whose Event is PUBLISHED
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

#### Scenario: Payment disputed

- **WHEN** Refund is called for a Paid Order of a CANCELLED Event that has an Open Dispute
- **THEN** it fails with FailedPrecondition, no money moves and the Order stays Paid

### Requirement: Fan refunded the full amount

Refund SHALL refund the price of the Order's Tickets that are still Issued — the Order's amount divided by its number of Tickets, times the number still Issued — to the fan's original payment with Order.CreateRefund for the Order's own refund, against the charge recorded on the Order's Settlement or, when none is recorded, the charge found by Order.GetProviderChargeID. Tickets the fan resold through official resale were already refunded less the resale fee and are not refunded again. When no Ticket of the Order is Issued, it SHALL issue no refund. It SHALL fail with FailedPrecondition when the Order's payment provider cannot issue refunds or the Order has no provider payment ID.

#### Scenario: Cancellation refund

- **WHEN** an event is cancelled and a 16000 yen Order is refunded
- **THEN** 16000 yen is refunded to the fan's card

#### Scenario: Cancellation after a resale

- **WHEN** an event is cancelled and a 10000 yen Order for 2 tickets, one of which was resold, is refunded
- **THEN** 5000 yen is refunded to the fan's card

#### Scenario: Every ticket resold

- **WHEN** an event is cancelled and every Ticket of the Order was resold
- **THEN** no refund is issued and the Order is recorded Refunded

#### Scenario: Dispute

- **WHEN** Refund is called with the reason Dispute
- **THEN** no refund is issued to the fan, because Refund fails with InvalidArgument before any money moves

### Requirement: Payout clawed back

Refund SHALL read the Order's Settlement with Settlement.GetByOrderID; every Paid Order has one. A missing Settlement SHALL be returned as Internal, since it means the stored records are inconsistent, and any other failure to read it SHALL be returned unchanged, with no money moved and nothing recorded. When it is Held, no payout is reversed and the Settlement is given to Order.CommitRefund as Held, so it becomes Reversed and is never paid out later. When it is already Reversed, as after every Ticket of the Order was resold, nothing is clawed back and no Settlement is given to Order.CommitRefund. A Releasing or Released Settlement SHALL be returned as Internal, with no money moved: a CANCELLED Event is never eligible for release and cannot be cancelled once its payout is due, so such a Settlement means the stored records are inconsistent.

#### Scenario: Payout not yet released

- **WHEN** the Order's Settlement is Held
- **THEN** no payout is reversed and the Settlement becomes Reversed

#### Scenario: Settlement given up by resales

- **WHEN** the Order's Settlement was Reversed because every Ticket was resold
- **THEN** nothing is clawed back and the Order is recorded Refunded

#### Scenario: Settlement unreadable

- **WHEN** Settlement.GetByOrderID fails with NotFound for a Paid Order
- **THEN** Refund fails with Internal, no money moves and the Order stays Paid

#### Scenario: Payout already released

- **WHEN** the Order's Settlement is Released
- **THEN** Refund fails with Internal, no money moves and the Order stays Paid

### Requirement: Refund recorded

After the money has moved, Refund SHALL record the refund with Order.CommitRefund — the Order Refunded with the reason Cancellation, the price of the Tickets still Issued, its provider refund ID and the current time, all of its Tickets Voided, its Settlement Reversed — and return the Refunded Order. When Order.CommitRefund fails with FailedPrecondition because another refund of the same Order got there first, Refund SHALL return the Order as read again with Order.Get. When a money movement fails, its error SHALL be returned and nothing is recorded; a retried Refund refunds at most once.

#### Scenario: Tickets voided
- **WHEN** an Order with 2 Issued Tickets is refunded
- **THEN** the Order is Refunded and both Tickets are Voided

#### Scenario: Cancellation refund recorded
- **WHEN** a 6000 yen Order for 2 tickets, one of which was resold, is refunded
- **THEN** the Order is recorded Refunded with the reason Cancellation and the amount 3000 yen

#### Scenario: Dispute recorded
- **WHEN** Refund is called with the reason Dispute
- **THEN** nothing is recorded; a lost or accepted dispute is recorded by DisputeUseCase.Settle

#### Scenario: Concurrent refund
- **WHEN** Order.CommitRefund fails with FailedPrecondition
- **THEN** Refund returns the Order as it is now stored

#### Scenario: Retry after a failure
- **WHEN** a refund failed after the fan was refunded and is run again
- **THEN** the fan is not refunded a second time and the refund is recorded
