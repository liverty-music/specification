# Order.CommitRefund

## Purpose

Records a completed refund: the Order becomes Refunded with its provider refund ID, all its Tickets become Voided, and its Settlement, if any, becomes Reversed with the provider payout reversal IDs of its splits.

## Requirements

### Requirement: Refund recorded together

CommitRefund SHALL set the Order to Refunded with the given provider refund ID, set every Ticket of the Order to Voided, and, when a Settlement is given, set it to Reversed and record each given split's provider payout reversal ID, all together or not at all. When no Settlement is given, only the Order and its Tickets change. It SHALL fail with FailedPrecondition when the given Settlement is already Reversed, and then changes nothing.

#### Scenario: Refund recorded

- **WHEN** CommitRefund is called for a Paid Order with 2 Issued Tickets and a Released Settlement
- **THEN** the Order is Refunded, both Tickets are Voided and the Settlement is Reversed with its provider payout reversal IDs

#### Scenario: No settlement

- **WHEN** CommitRefund is called without a Settlement
- **THEN** the Order is Refunded and its Tickets are Voided

#### Scenario: Settlement already reversed

- **WHEN** the given Settlement is already Reversed
- **THEN** CommitRefund fails with FailedPrecondition and changes nothing

#### Scenario: Failure changes nothing

- **WHEN** recording any part of the refund fails
- **THEN** the Order, its Tickets and its Settlement keep their earlier states
