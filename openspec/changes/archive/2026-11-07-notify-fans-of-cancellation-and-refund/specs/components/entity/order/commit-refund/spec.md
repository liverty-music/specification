## MODIFIED Requirements

### Requirement: Refund recorded together

CommitRefund SHALL take an Order, the refund's reason (Cancellation or Dispute), the amount refunded to the user's card, the provider refund ID and the time, and SHALL set the Order to Refunded with that reason, amount, provider refund ID and refund time, set every Issued Ticket of the Order to Voided, set every Listed ResaleListing of those Tickets to Cancelled, and, when a Settlement is given, set it to Reversed and record each given split's provider payout reversal ID, all together or not at all. The amount is 0 and the provider refund ID is empty when nothing was left to refund or the reason is Dispute. When no Settlement is given, only the Order, its Tickets and their listings change. A Ticket already Voided by a resale and its Sold listing stay as they are. It SHALL fail with InvalidArgument, changing nothing, when no reason is given or the amount is below 0, and with FailedPrecondition when the given Settlement is already Reversed, and then changes nothing. When the Order is not Paid, because an earlier call already made it Refunded, CommitRefund SHALL change nothing and keep the first refund's reason, amount, provider refund ID and refund time; with a Settlement given it fails with FailedPrecondition as above.

#### Scenario: Refund recorded
- **WHEN** CommitRefund is called for a Paid Order with 2 Issued Tickets and a Released Settlement, with the reason Cancellation and the amount 6000 yen
- **THEN** the Order is Refunded with the reason Cancellation, the amount 6000 yen, its provider refund ID and the refund time, both Tickets are Voided and the Settlement is Reversed with its provider payout reversal IDs

#### Scenario: Ticket on resale
- **WHEN** CommitRefund is called for a Paid Order with 2 Issued Tickets, one of them Listed for resale
- **THEN** both Tickets are Voided and the listing is Cancelled

#### Scenario: Ticket resold earlier
- **WHEN** CommitRefund is called for a Paid Order with 1 Issued Ticket and 1 Ticket Voided by a resale
- **THEN** the Issued Ticket is Voided and the resold Ticket's Sold listing is unchanged

#### Scenario: No settlement
- **WHEN** CommitRefund is called without a Settlement
- **THEN** the Order is Refunded and its Tickets are Voided

#### Scenario: Dispute recorded
- **WHEN** CommitRefund is called with the reason Dispute, the amount 0 and no provider refund ID
- **THEN** the Order is Refunded with the reason Dispute and the amount 0

#### Scenario: Reason missing
- **WHEN** CommitRefund is called without a reason
- **THEN** it fails with InvalidArgument and the Order stays Paid

#### Scenario: Amount below zero
- **WHEN** CommitRefund is called with an amount below 0
- **THEN** it fails with InvalidArgument and the Order stays Paid

#### Scenario: Order already refunded
- **WHEN** CommitRefund is called without a Settlement for an Order that is already Refunded, with another amount
- **THEN** nothing changes and the first refund's reason, amount and time are kept

#### Scenario: Settlement already reversed
- **WHEN** the given Settlement is already Reversed
- **THEN** CommitRefund fails with FailedPrecondition and changes nothing

#### Scenario: Failure changes nothing
- **WHEN** recording any part of the refund fails
- **THEN** the Order, its Tickets, their listings and its Settlement keep their earlier states

## ADDED Requirements

### Requirement: A recorded refund is announced with it

When CommitRefund makes the Order Refunded, it SHALL announce the Order as refunded together with the refund: both are stored or neither is. When the Order is already Refunded, CommitRefund SHALL announce nothing. When the announcement cannot be recorded, CommitRefund SHALL fail with Unavailable and change nothing.

#### Scenario: Refund announced
- **WHEN** CommitRefund makes a Paid Order Refunded
- **THEN** the Order is announced as refunded once

#### Scenario: Recorded twice
- **WHEN** CommitRefund is called again for an Order that is already Refunded
- **THEN** nothing is announced and the first refund's reason, amount and time are kept

#### Scenario: Announcement cannot be recorded
- **WHEN** the refund announcement cannot be recorded
- **THEN** CommitRefund fails with Unavailable and the Order stays Paid
