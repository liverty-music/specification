# Spec Delta

## Purpose

Records that the money outcome of a Lost or Accepted Dispute was applied, with the claw-backs made for it alone, so the Order is no longer held for it.

## ADDED Requirements

### Requirement: Settled once

MarkSettled SHALL take a Lost or Accepted Dispute, the settle time and the provider payout reversal IDs of the claw-backs made for it alone (none when there were none), and record them. When the Dispute already has a settle time it SHALL change nothing. It SHALL fail with FailedPrecondition, changing nothing, when the Dispute is Open, Contested or Won, and with NotFound when no Dispute has the id.

#### Scenario: Partial dispute settled after the payout
- **WHEN** MarkSettled is called for a Lost partial Dispute with one provider payout reversal ID
- **THEN** the Dispute has its settle time and that provider payout reversal ID

#### Scenario: Won dispute
- **WHEN** MarkSettled is called for a Won Dispute
- **THEN** it fails with FailedPrecondition and nothing changes
