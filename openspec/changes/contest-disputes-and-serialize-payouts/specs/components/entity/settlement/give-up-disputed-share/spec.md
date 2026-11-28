# Spec Delta

## Purpose

Lowers a Held Settlement's splits by the Organizer's share of a partial Dispute that was lost or accepted before the payout, and records the Dispute settled with it.

## ADDED Requirements

### Requirement: Share given up once, with the dispute settled

GiveUpDisputedShare SHALL take a Held Settlement and a Lost or Accepted partial Dispute of its Order, lower its splits by the Organizer's share of the Dispute (spread over the splits in proportion to their amounts, each rounded down), and record the Dispute's settle time, all together or not at all. When nothing would be left to pay out, the Settlement SHALL become Reversed instead. When the Dispute already has a settle time it SHALL change nothing. It SHALL fail with FailedPrecondition, changing nothing, when the Settlement is not Held or the Dispute is not Lost or Accepted, and with NotFound when either does not exist.

#### Scenario: Half of an order lost before the payout
- **WHEN** GiveUpDisputedShare is called for a Held Settlement with a split of 9500 yen and a Lost partial Dispute of 5000 yen on an Order of 10000 yen
- **THEN** the split is 4750 yen and the Dispute has its settle time

#### Scenario: Settlement claimed meanwhile
- **WHEN** the Settlement is Releasing
- **THEN** GiveUpDisputedShare fails with FailedPrecondition and nothing changes
