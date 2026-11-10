## MODIFIED Requirements

### Requirement: Each ended entry is announced with the change

EndEnteredByEvent SHALL announce each entry it makes Lost as lost (LotteryEntry.Lost), as it is after the change, together with the change: both are stored or neither is. An entry it leaves unchanged SHALL NOT be announced. When an announcement cannot be recorded, EndEnteredByEvent SHALL fail with Unavailable and change nothing. Each announcement is what product analytics records as one "lottery result" signal for the fan of the entry's Order.

#### Scenario: Two entries ended
- **WHEN** EndEnteredByEvent makes two entries Lost
- **THEN** both entries are announced as lost, each carrying its entry Lost with the lost reason "concert cancelled"

#### Scenario: Called again announces nothing
- **WHEN** EndEnteredByEvent is called again for an Event whose entries it already ended
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded
- **WHEN** an entry's announcement cannot be recorded
- **THEN** EndEnteredByEvent fails with Unavailable, every entry stays Entered and every Order stays Pending
