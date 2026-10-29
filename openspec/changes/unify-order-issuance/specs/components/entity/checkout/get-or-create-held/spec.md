## ADDED Requirements

### Requirement: A new hold and the checkouts it ends are announced with it

When GetOrCreateHeld creates a Held Checkout, it SHALL announce it as held, and announce each Checkout it makes Released as released and each it makes Expired as expired, each carrying the Checkout as it is after the change, together with the change: all of it is stored and announced, or nothing is. When it returns an existing holding Checkout it SHALL announce nothing. When an announcement cannot be recorded, GetOrCreateHeld SHALL fail with Unavailable and change nothing.

#### Scenario: Count changed
- **WHEN** a fan holding a Checkout for 2 tickets starts again for 3
- **THEN** the 2-ticket Checkout is announced as released and the new 3-ticket Checkout as held

#### Scenario: Same hold resumed
- **WHEN** a fan starts again with the same count while holding
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded
- **WHEN** the announcement of a new hold cannot be recorded
- **THEN** GetOrCreateHeld fails with Unavailable, no Checkout is created and the earlier hold stays Held
