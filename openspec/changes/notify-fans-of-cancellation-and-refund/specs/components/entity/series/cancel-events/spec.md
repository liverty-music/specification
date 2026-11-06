## ADDED Requirements

### Requirement: Each cancelled event is announced with it

When CancelEvents makes an Event CANCELLED, it SHALL announce that Event as cancelled together with the change: the cancellation and its announcement are stored or neither is. It SHALL announce nothing for a DRAFT Event it removes. When an announcement cannot be recorded, CancelEvents SHALL fail with Unavailable and change nothing.

#### Scenario: Two dates cancelled
- **WHEN** CancelEvents makes two PUBLISHED Events of a Series CANCELLED
- **THEN** each of the two Events is announced as cancelled once

#### Scenario: Draft removed
- **WHEN** CancelEvents removes a DRAFT Event
- **THEN** nothing is announced for it

#### Scenario: Announcement cannot be recorded
- **WHEN** the announcement of a cancelled Event cannot be recorded
- **THEN** CancelEvents fails with Unavailable and every given Event keeps its state
