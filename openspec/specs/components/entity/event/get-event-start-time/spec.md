# Event.GetEventStartTime

## Purpose

Returns an Event's current start time, read afresh so that a 延期 (postponement) is seen at once.

## Requirements

### Requirement: Current start time or none

GetEventStartTime SHALL return the Event's current start time, and no time when the start is not yet known. It SHALL fail with NotFound when no Event has the id.

#### Scenario: Known start

- **WHEN** the Event starts at 2026-11-03 18:00
- **THEN** it returns 2026-11-03 18:00

#### Scenario: Start not announced

- **WHEN** the Event has no start time
- **THEN** it returns no time and no error

#### Scenario: Unknown event

- **WHEN** no Event has the id
- **THEN** it fails with NotFound
