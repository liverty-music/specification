## MODIFIED Requirements

### Requirement: A reverted win is announced with the change

When RevertWin makes an entry Lost, it SHALL announce the entry as lost (LotteryEntry.Lost), as it is after the change, together with the change: both are stored or neither is. When it changes nothing it SHALL announce nothing. When the announcement cannot be recorded, RevertWin SHALL fail with Unavailable and change nothing. The announcement is what product analytics records as the entry's "lottery result" signal for the lost win.

#### Scenario: Win reverted and announced
- **WHEN** RevertWin makes a Won entry Lost
- **THEN** the entry is announced as lost once, carrying it Lost with the lost reason RevertWin was given

#### Scenario: Already reverted announces nothing
- **WHEN** RevertWin is called again for an entry it already made Lost
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded
- **WHEN** the announcement of a reverted win cannot be recorded
- **THEN** RevertWin fails with Unavailable, the entry stays Won and its Order stays Pending
