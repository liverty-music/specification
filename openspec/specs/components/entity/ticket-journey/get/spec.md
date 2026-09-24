# TicketJourney.Get

## Purpose

Returns one fan's ticket journey for one event, so a caller can learn the fan's current status before changing it.

## Requirements

### Requirement: Get returns the fan's journey for the event

Get SHALL return the journey of the given fan for the given event, with its current status. It SHALL fail with NotFound when that fan has no journey for that event.

#### Scenario: The fan has a journey

- **WHEN** the fan has a journey with status Applied for the event
- **THEN** Get returns that journey with status Applied

#### Scenario: The fan has no journey

- **WHEN** the fan has no journey for the event
- **THEN** Get fails with NotFound

#### Scenario: Another fan's journey is not returned

- **WHEN** only a different fan has a journey for the event
- **THEN** Get for this fan fails with NotFound
