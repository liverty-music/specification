## MODIFIED Requirements

### Requirement: Each recorded entry is announced with the draw

PersistDrawOutcome SHALL announce each entry it makes Won as won (ResaleEntry.Won), each it makes Lapsed as lapsed (ResaleEntry.Lapsed) and each it makes Lost as lost (ResaleEntry.Lost), as it is after the draw, together with the outcome: the outcome and its announcements are stored together or not at all. When an announcement cannot be recorded, PersistDrawOutcome SHALL fail with Unavailable and record nothing.

#### Scenario: Three entries recorded
- **WHEN** a draw records one entry Won, one Lapsed and one Lost
- **THEN** the entries are announced as won, lapsed and lost, one announcement each

#### Scenario: Announcement cannot be recorded
- **WHEN** an entry's announcement cannot be recorded
- **THEN** PersistDrawOutcome fails with Unavailable and no entry, listing or Order changes
