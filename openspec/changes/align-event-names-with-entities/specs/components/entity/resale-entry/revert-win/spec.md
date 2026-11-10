## MODIFIED Requirements

### Requirement: A reverted resale win is announced with the change

When RevertWin makes an entry Lost, it SHALL announce the entry as lost (ResaleEntry.Lost), as it is after the change, together with the change: both are stored or neither is. When it changes nothing it SHALL announce nothing. When the announcement cannot be recorded, RevertWin SHALL fail with Unavailable and change nothing.

#### Scenario: Win reverted and announced
- **WHEN** RevertWin makes a Won entry Lost
- **THEN** the entry is announced as lost once, carrying it as Lost

#### Scenario: Announcement cannot be recorded
- **WHEN** the announcement of a reverted win cannot be recorded
- **THEN** RevertWin fails with Unavailable, the entry stays Won and its Order stays Pending
