# components/entity/event/get Specification

## Purpose
Reads one Event's current date and times, read afresh so that a date or time filled in after publish is seen at once.

## Requirements

### Requirement: Current date and times of an event

Get SHALL return the Event's id, current local date, open time, start time and publish state, an unknown time being returned as none and the publish state being returned as none for an Event of a discovered Series. It SHALL fail with NotFound when no Event has the id.

#### Scenario: Event with both times

- **WHEN** the Event is on 2026-11-20, opens at 18:00 and starts at 19:00
- **THEN** Get returns 2026-11-20, 18:00 and 19:00

#### Scenario: Start time filled in later

- **WHEN** the Event on 2026-11-20 had no start time and its start time is later set to 19:00
- **THEN** Get returns 19:00 as the start time

#### Scenario: Cancelled event

- **WHEN** the Event of a first-party Series is CANCELLED
- **THEN** Get returns the publish state CANCELLED

#### Scenario: Discovered event

- **WHEN** the Event belongs to a Series found by discovery
- **THEN** Get returns no publish state

#### Scenario: Unknown event

- **WHEN** no Event has the id
- **THEN** Get fails with NotFound
