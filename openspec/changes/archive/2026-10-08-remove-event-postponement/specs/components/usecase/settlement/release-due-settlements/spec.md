# Spec Delta

## ADDED Requirements

### Requirement: Release 7 days after the event's current start

ReleaseDueSettlements SHALL run every 5 minutes over the Settlements from Settlement.ListHeld. For each, it SHALL read the Order with Order.Get and the event's current start time with Event.GetEventStartTime, and SHALL withhold the Settlement unless it is eligible for release with a dispute buffer of 7 days. Because the start time is read on every run, a start time that is filled in after the purchase is used from the next run. A Settlement whose event does not exist is skipped.

#### Scenario: Before the event plus 7 days

- **WHEN** the event started 3 days ago
- **THEN** the Settlement stays Held

#### Scenario: Event start unknown

- **WHEN** the event has no start time
- **THEN** the Settlement stays Held

#### Scenario: Start time filled in after the purchase

- **WHEN** the event had no start time when the Order was paid and its start time is later set to 8 days ago
- **THEN** on the next run the Settlement is eligible for release

## REMOVED Requirements

### Requirement: Release after the event plus 7 days

**Reason**: Replaced by "Release 7 days after the event's current start", which keeps the same gate and the per-run start-time read but no longer describes 延期 (postponement), a state an Event cannot be in. Its "Event postponed" scenario is dropped and a scenario for a start time filled in after the purchase is added.
**Migration**: None. The release gate is unchanged.
