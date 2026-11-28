# Spec Delta

## MODIFIED Requirements

### Requirement: Refund recorded together

CommitRefund SHALL take an Order, the refund's reason (Cancellation or Dispute), the amount refunded to the user's card, the provider refund ID and the time, and, optionally, a Settlement with the status the caller read it in (Held, when nothing was clawed back, or Released, when every paid split was) and each split's provider payout reversal ID, and, for the reason Dispute, the Dispute it settles. It SHALL set the Order to Refunded with that reason, amount, provider refund ID and refund time, set every Issued Ticket of the Order to Voided, set every Listed ResaleListing of those Tickets to Cancelled, and, when a Settlement is given, set it to Reversed from the status given and record each given split's provider payout reversal ID, and, when a Dispute is given, record its settle time, all together or not at all. The amount is 0 and the provider refund ID is empty when nothing was left to refund or the reason is Dispute on a chargeback, where the money went back to the fan through the card issuer; for an accepted inquiry the amount and provider refund ID are those of the refund the platform made. When no Settlement is given, only the Order, its Tickets and their listings change. A Ticket already Voided by a resale and its Sold listing stay as they are. It SHALL fail with InvalidArgument, changing nothing, when no reason is given or the amount is below 0, and with FailedPrecondition when the given Settlement is no longer in the status given (Releasing, Reversed, or the other of Held and Released), and then changes nothing. When the Order is already Refunded, because an earlier call made it so, CommitRefund SHALL change nothing else, keep the first refund's reason, amount, provider refund ID and refund time, and still record a given Dispute's settle time; with a Settlement given it fails with FailedPrecondition when that Settlement is no longer in the status given. When the Order is Pending or Void, CommitRefund SHALL fail with FailedPrecondition and change nothing: such an Order was never paid, so a refund recorded against it is an error, not a repeat. When no Order has the given id, CommitRefund SHALL fail with NotFound and change nothing.

#### Scenario: Refund recorded
- **WHEN** CommitRefund is called for a Paid Order with 2 Issued Tickets and a Settlement read as Released, with the reason Dispute, the amount 0 and the provider payout reversal IDs
- **THEN** the Order is Refunded with the reason Dispute, the amount 0 and the refund time, both Tickets are Voided and the Settlement is Reversed with its provider payout reversal IDs

#### Scenario: Ticket on resale
- **WHEN** CommitRefund is called for a Paid Order with 2 Issued Tickets, one of them Listed for resale
- **THEN** both Tickets are Voided and the listing is Cancelled

#### Scenario: Ticket resold earlier
- **WHEN** CommitRefund is called for a Paid Order with 1 Issued Ticket and 1 Ticket Voided by a resale
- **THEN** the Issued Ticket is Voided and the resold Ticket's Sold listing is unchanged

#### Scenario: No settlement
- **WHEN** CommitRefund is called without a Settlement
- **THEN** the Order is Refunded and its Tickets are Voided

#### Scenario: Cancellation refund recorded
- **WHEN** CommitRefund is called for a Paid Order with a Settlement read as Held, the reason Cancellation and the amount 6000 yen
- **THEN** the Order is Refunded with the reason Cancellation, the amount 6000 yen and its provider refund ID, and the Settlement is Reversed

#### Scenario: Dispute recorded
- **WHEN** CommitRefund is called with the reason Dispute, the amount 0, no provider refund ID and the Lost Dispute it settles
- **THEN** the Order is Refunded with the reason Dispute and the amount 0, and the Dispute has its settle time

#### Scenario: Second dispute on a refunded order
- **WHEN** CommitRefund is called without a Settlement for an Order already Refunded, with another Lost Dispute
- **THEN** the first refund is kept and that Dispute has its settle time

#### Scenario: Reason missing
- **WHEN** CommitRefund is called without a reason
- **THEN** it fails with InvalidArgument and the Order stays Paid

#### Scenario: Amount below zero
- **WHEN** CommitRefund is called with an amount below 0
- **THEN** it fails with InvalidArgument and the Order stays Paid

#### Scenario: Order already refunded
- **WHEN** CommitRefund is called without a Settlement for an Order that is already Refunded, with another amount
- **THEN** nothing changes and the first refund's reason, amount and time are kept

#### Scenario: Order never paid
- **WHEN** CommitRefund is called for an Order that is Pending or Void
- **THEN** it fails with FailedPrecondition, nothing changes and nothing is announced

#### Scenario: Unknown order
- **WHEN** CommitRefund is called with an id no Order has
- **THEN** it fails with NotFound and nothing is announced

#### Scenario: Settlement already reversed
- **WHEN** the given Settlement is already Reversed
- **THEN** CommitRefund fails with FailedPrecondition and changes nothing

#### Scenario: Settlement claimed after it was read
- **WHEN** a Settlement read as Held is given and a release has since made it Releasing
- **THEN** CommitRefund fails with FailedPrecondition, the Order stays Paid and the Settlement stays Releasing

#### Scenario: Failure changes nothing
- **WHEN** recording any part of the refund fails
- **THEN** the Order, its Tickets, their listings and its Settlement keep their earlier states
