# Spec Delta

## ADDED Requirements

### Requirement: Free for a draw

A listing SHALL be free for a draw at a time when it is open at that time and no ResaleEntry is allocated to it, or the entry allocated to it is Lost. Only a free listing can be allocated by a draw or withdrawn, so a listing is withdrawable only while it is free.

#### Scenario: Never allocated
- **WHEN** an open listing has no entry
- **THEN** it is free for a draw

#### Scenario: Won by an entry being charged
- **WHEN** an open listing is allocated to a Won entry
- **THEN** it is not free

#### Scenario: Winner could not be charged
- **WHEN** an open listing's entry became Lost after it won
- **THEN** it is free for the next draw

## MODIFIED Requirements

### Requirement: Resale deadline

A listing's deadline SHALL be its Ticket's event's last resale draw: 12:00 Japan time on the event's day, or 3 hours before the event's current start time, when admission opens, if that is earlier. Resale closes at the last draw, so nothing is listed, applied for or left open after it.

#### Scenario: Event with an open time
- **WHEN** the event opens its doors at 18:00 and starts at 19:00
- **THEN** the deadline is 12:00 that day

#### Scenario: Event without an open time
- **WHEN** the event has no open time and starts at 14:00
- **THEN** the deadline is 11:00 that day

## REMOVED Requirements

### Requirement: Withdrawable while open

**Reason**: A listing a draw allocated to a Won entry is being bought and can no longer be withdrawn.
**Migration**: See "Free for a draw": only a free listing can be withdrawn.
