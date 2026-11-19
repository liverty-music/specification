# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: Resale deadline`
- TO: `### Requirement: Close time`

## MODIFIED Requirements

### Requirement: Close time

A listing's close time SHALL be its Ticket's event's last resale draw: 12:00 on the event's day in the time zone of the event's Venue, or 3 hours before the event's current start time, when admission opens, if that is earlier. Resale closes at the last draw, so nothing is listed, applied for or left open after it.

#### Scenario: Event with an open time
- **WHEN** the event opens its doors at 18:00 and starts at 19:00
- **THEN** the close time is 12:00 that day

#### Scenario: Event without an open time
- **WHEN** the event has no open time and starts at 14:00
- **THEN** the close time is 11:00 that day

### Requirement: Open and expired

A listing SHALL be open at a time when it is Listed and the time is before its close time. A Listed listing at or after its close time SHALL be expired: it can no longer be held, bought or withdrawn, and its Ticket stays the user's, except that the event's last draw, which runs at the close time, still allocates it ("Free for a draw").

#### Scenario: Before the close time
- **WHEN** a Listed listing with the close time 16:00 is checked at 15:59
- **THEN** it is open

#### Scenario: At the close time
- **WHEN** the same listing is checked at 16:00
- **THEN** it is expired and not open

#### Scenario: Sold listing
- **WHEN** a Sold listing is checked before its close time
- **THEN** it is not open

### Requirement: Free for a draw

A listing SHALL be free for a draw at a draw time when it is Listed and the draw time is not after its close time, so the event's last draw, which runs at the close time, still allocates it, and no ResaleEntry is allocated to it, or the entry allocated to it is Lost. Only a free listing can be allocated by a draw. A listing SHALL be withdrawable only while it is open and free for a draw.

#### Scenario: Never allocated
- **WHEN** an open listing has no entry
- **THEN** it is free for a draw

#### Scenario: Won by an entry being charged
- **WHEN** an open listing is allocated to a Won entry
- **THEN** it is not free

#### Scenario: Winner could not be charged
- **WHEN** an open listing's entry became Lost after it won
- **THEN** it is free for the next draw
