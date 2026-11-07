## MODIFIED Requirements

### Requirement: Refund recorded

After the money has moved, Refund SHALL record the refund with Order.CommitRefund — the Order Refunded with the reason, the amount refunded to the fan's card (the price of the Tickets still Issued for the reason Cancellation, 0 for the reason Dispute), its provider refund ID and the current time, all of its Tickets Voided, its Settlement Reversed — and return the Refunded Order. When Order.CommitRefund fails with FailedPrecondition because another refund of the same Order got there first, Refund SHALL return the Order as read again with Order.Get. When a money movement fails, its error SHALL be returned and nothing is recorded; a retried Refund refunds and reverses at most once.

#### Scenario: Tickets voided
- **WHEN** an Order with 2 Issued Tickets is refunded
- **THEN** the Order is Refunded and both Tickets are Voided

#### Scenario: Cancellation refund recorded
- **WHEN** a 6000 yen Order for 2 tickets, one of which was resold, is refunded with the reason Cancellation
- **THEN** the Order is recorded Refunded with the reason Cancellation and the amount 3000 yen

#### Scenario: Dispute recorded
- **WHEN** an Order is refunded with the reason Dispute
- **THEN** the Order is recorded Refunded with the reason Dispute and the amount 0

#### Scenario: Concurrent refund
- **WHEN** Order.CommitRefund fails with FailedPrecondition
- **THEN** Refund returns the Order as it is now stored

#### Scenario: Retry after a failure
- **WHEN** a refund failed after the fan was refunded and is run again
- **THEN** the fan is not refunded a second time and the refund is recorded
