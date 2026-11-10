## MODIFIED Requirements

### Requirement: Each drawn entry is announced with the outcome

PersistDrawOutcome SHALL announce each entry it sets Won as won (LotteryEntry.Won) and each it sets Lost as lost (LotteryEntry.Lost), as it is after the draw, together with the outcome: the outcome and its announcements are stored together or not at all. An entry it leaves unchanged SHALL NOT be announced. When an announcement cannot be recorded, PersistDrawOutcome SHALL fail with Unavailable and record nothing. Each announcement is what product analytics records as one "lottery result" signal for the fan of the entry's Order.

#### Scenario: Two entries, one place
- **WHEN** PersistDrawOutcome records one entry Won and one entry Lost
- **THEN** the Won entry is announced as won and the Lost entry as lost

#### Scenario: Recorded again announces nothing
- **WHEN** PersistDrawOutcome is called again with an outcome already recorded
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded
- **WHEN** an entry's announcement cannot be recorded
- **THEN** PersistDrawOutcome fails with Unavailable and no entry, lost reason or Order status is changed
