# Spec Delta

## MODIFIED Requirements

### Requirement: Pay out and mark Released

For an eligible Settlement with an Active payout account, ReleaseDueSettlements SHALL fail that Settlement, leaving it Held, when its splits break the Settlement split rules against the Order's amount. Otherwise it SHALL claim it with Settlement.Claim under a new release claim and start SettlementUseCase.Release for the Order and that claim, which pays it out. When Settlement.Claim fails with FailedPrecondition, because the Settlement is no longer Held or its Order got an open or unsettled Dispute, the Settlement is skipped without error. On every run it SHALL also list the Releasing Settlements with Settlement.ListReleasing and start SettlementUseCase.Release for each one's Order and release claim, which starts nothing when that Release already ran, so a claim whose Release was never started is paid out by a later run.

#### Scenario: Settlement released

- **WHEN** a Held Settlement's event started 8 days ago and the Organizer's payout account is Active
- **THEN** it is claimed, SettlementUseCase.Release starts for it, its split is paid to the Organizer's payout account and it is Released

#### Scenario: Invalid splits

- **WHEN** a due Settlement has no split
- **THEN** nothing is paid and it stays Held

#### Scenario: Released concurrently

- **WHEN** Settlement.Claim fails with FailedPrecondition
- **THEN** the Settlement is skipped and no error is raised

#### Scenario: Claimed but not started

- **WHEN** a run claimed a Settlement and stopped before starting its Release
- **THEN** the next run finds it Releasing and starts its Release

### Requirement: One failure does not block the others

A Settlement whose claim or release fails SHALL NOT stop the others. When Settlement.ListHeld or Settlement.ListReleasing fails, ReleaseDueSettlements SHALL fail with that error.

#### Scenario: One payout fails

- **WHEN** the release of one Settlement fails
- **THEN** the other due Settlements are still released

## REMOVED Requirements

### Requirement: Release 7 days after the event's current start

**Reason**: An Event can no longer be cancelled from 24 hours after its start, 6 days before its payout is due, so the cases of a cancellation racing a payout ("Cancelled after the run read the event", "Cancelled before a failed release is recorded") cannot happen; and an open or unsettled Dispute now withholds the payout.
**Migration**: Replaced by "Release 7 days after the event's current start, not while disputed" below. No data changes.

## ADDED Requirements

### Requirement: Release 7 days after the event's current start, not while disputed

ReleaseDueSettlements SHALL run every 5 minutes over the Settlements from Settlement.ListHeld. For each, it SHALL read the Order with Order.Get, the event's current publish state with Event.Get, the event's current start time with Event.GetEventStartTime and the Order's Disputes with Dispute.ListByOrder, and SHALL withhold the Settlement, without failing it, unless it is eligible for release with a dispute buffer of 7 days. All of them are read for each Settlement on every run, so a start time filled in after the purchase, a cancellation made after the purchase and a dispute opened, closed or settled apply from the next such read. The Settlement of a CANCELLED Event is withheld on every run and stays Held. A Settlement whose Order has an open or unsettled Dispute is withheld until no such Dispute is left. A Settlement whose event does not exist is skipped.

#### Scenario: Before the event plus 7 days

- **WHEN** the event started 3 days ago
- **THEN** the Settlement stays Held

#### Scenario: Event start unknown

- **WHEN** the event has no start time
- **THEN** the Settlement stays Held

#### Scenario: Start time filled in after the purchase

- **WHEN** the event had no start time when the Order was paid and its start time is later set to 8 days ago
- **THEN** on the next run the Settlement is eligible for release

#### Scenario: Cancelled event past the buffer

- **WHEN** a Held Settlement's event is CANCELLED, it started 8 days ago and the Organizer's payout account is Active
- **THEN** nothing is paid, no error is raised for the Settlement and it stays Held

#### Scenario: Disputed payment past the buffer

- **WHEN** a Held Settlement's event started 8 days ago and its Order has a Contested Dispute
- **THEN** it is not claimed and stays Held

#### Scenario: Lost dispute not yet settled

- **WHEN** a Held Settlement's Order has a Lost Dispute whose settlement has not been applied yet
- **THEN** it is not claimed and stays Held until the Dispute is settled

#### Scenario: Dispute won

- **WHEN** the Order's only Dispute becomes Won
- **THEN** the next run claims and releases the Settlement
