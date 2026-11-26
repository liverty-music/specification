## MODIFIED Requirements

### Requirement: Release 7 days after the event's current start

ReleaseDueSettlements SHALL run every 5 minutes over the Settlements from Settlement.ListHeld. For each, it SHALL read the Order with Order.Get, the event's current publish state with Event.Get and the event's current start time with Event.GetEventStartTime, and SHALL withhold the Settlement, without failing it, unless it is eligible for release with a dispute buffer of 7 days. Both are read for each Settlement on every run, before any of its splits is paid, so a start time that is filled in after the purchase and a cancellation made after the purchase apply from the next such read. The Settlement of a CANCELLED Event is withheld on every run and stays Held. A cancellation stored after a run has read the event does not stop that run's payout of the Settlement, which becomes Released like any other. When a run has paid a split but cannot record the release, and the event is then CANCELLED, the Settlement stays Held with the payout unrecorded, and no later run records it. A Settlement whose event does not exist is skipped.

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

#### Scenario: Cancelled after the run read the event

- **WHEN** a due Settlement's event is read as PUBLISHED and is cancelled before the split is paid
- **THEN** that run pays the split and the Settlement is Released

#### Scenario: Cancelled before a failed release is recorded

- **WHEN** a run paid a Settlement's split, Settlement.MarkReleased failed with Unavailable, and the event is cancelled before the next run
- **THEN** the next run pays nothing, does not call Settlement.MarkReleased and the Settlement stays Held
