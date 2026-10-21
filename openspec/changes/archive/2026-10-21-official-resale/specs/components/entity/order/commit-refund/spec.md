## MODIFIED Requirements

### Requirement: Refund recorded together

CommitRefund SHALL set the Order to Refunded with the given provider refund ID, set every Issued Ticket of the Order to Voided, set every Listed ResaleListing of those Tickets to Cancelled, and, when a Settlement is given, set it to Reversed and record each given split's provider payout reversal ID, all together or not at all. The provider refund ID is empty when nothing was left to refund. When no Settlement is given, only the Order, its Tickets and their listings change. A Ticket already Voided by a resale and its Sold listing stay as they are. It SHALL fail with FailedPrecondition when the given Settlement is already Reversed, and then changes nothing.

#### Scenario: Refund recorded

- **WHEN** CommitRefund is called for a Paid Order with 2 Issued Tickets and a Released Settlement
- **THEN** the Order is Refunded, both Tickets are Voided and the Settlement is Reversed with its provider payout reversal IDs

#### Scenario: Ticket on resale

- **WHEN** CommitRefund is called for a Paid Order with 2 Issued Tickets, one of them Listed for resale
- **THEN** both Tickets are Voided and the listing is Cancelled

#### Scenario: Ticket resold earlier

- **WHEN** CommitRefund is called for a Paid Order with 1 Issued Ticket and 1 Ticket Voided by a resale
- **THEN** the Issued Ticket is Voided and the resold Ticket's Sold listing is unchanged

#### Scenario: No settlement

- **WHEN** CommitRefund is called without a Settlement
- **THEN** the Order is Refunded and its Tickets are Voided

#### Scenario: Settlement already reversed

- **WHEN** the given Settlement is already Reversed
- **THEN** CommitRefund fails with FailedPrecondition and changes nothing

#### Scenario: Failure changes nothing

- **WHEN** recording any part of the refund fails
- **THEN** the Order, its Tickets, their listings and its Settlement keep their earlier states
