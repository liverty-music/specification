## MODIFIED Requirements

### Requirement: Resale deadline

A listing's deadline SHALL be its Ticket's event's last resale draw: 12:00 on the event's day in the time zone of the event's Venue, or 3 hours before the event's current start time, when admission opens, if that is earlier. Resale closes at the last draw, so nothing is listed, applied for or left open after it.

#### Scenario: Event with an open time
- **WHEN** the event opens its doors at 18:00 and starts at 19:00
- **THEN** the deadline is 12:00 that day

#### Scenario: Event without an open time
- **WHEN** the event has no open time and starts at 14:00
- **THEN** the deadline is 11:00 that day
