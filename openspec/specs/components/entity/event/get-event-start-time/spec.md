# Event.GetEventStartTime

## Purpose

Returns an Event's current start time with its local date and its Venue's time zone, read afresh so that a start time filled in after publish is seen at once.

## Requirements

### Requirement: Current start time or none

GetEventStartTime SHALL return the Event's current start time, a time of day, together with its current local date and the time zone of its Venue, so the caller can compute the start's instant; when the start is not yet known it SHALL return no time, still with the local date and the Venue's time zone. It SHALL fail with NotFound when no Event has the id.

#### Scenario: Known start

- **WHEN** the Event at a Venue in Asia/Tokyo is on 2026-11-03 and starts at 18:00
- **THEN** it returns the local date 2026-11-03, the start time 18:00 and the time zone Asia/Tokyo

#### Scenario: Show abroad

- **WHEN** the Event at a Venue in Asia/Seoul is on 2026-11-20 and starts at 18:30
- **THEN** it returns the local date 2026-11-20, the start time 18:30 and the time zone Asia/Seoul

#### Scenario: Start not announced

- **WHEN** the Event at a Venue in Asia/Tokyo has no start time
- **THEN** it returns its local date, no time, the time zone Asia/Tokyo and no error

#### Scenario: Unknown event

- **WHEN** no Event has the id
- **THEN** it fails with NotFound
