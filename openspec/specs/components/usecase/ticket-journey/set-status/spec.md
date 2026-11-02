# Set Status

## Purpose

Records a fan's ticket journey status for one event at the fan's request, creating the journey or replacing its status through TicketJourney.Upsert, which announces every actual status change for product analytics.

## Requirements

### Requirement: SetStatus records the fan's status

When a fan sets a status for an event, SetStatus SHALL record the given status through TicketJourney.Upsert. It accepts any of the five journey statuses whatever the current status is. When TicketJourney.Upsert fails, SetStatus SHALL fail with that error.

#### Scenario: First status for an event

- **WHEN** the fan has no journey for the event and sets Tracking
- **THEN** the fan's journey for the event is recorded as Tracking

#### Scenario: Changing an existing status

- **WHEN** the fan's journey for the event is Applied and the fan sets Unpaid
- **THEN** the fan's journey for the event is recorded as Unpaid

#### Scenario: Recording the status fails

- **WHEN** TicketJourney.Upsert fails with Unavailable
- **THEN** SetStatus fails with Unavailable and the journey stays as it was
