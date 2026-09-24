# TicketJourney.Delete

## Purpose

Removes a fan's ticket journey for one event, so the event goes back to having no status for that fan.

## Requirements

### Requirement: Delete removes the journey and is idempotent

Delete SHALL remove the given fan's journey for the given event and SHALL leave every other journey unchanged. Deleting a journey that does not exist SHALL succeed and change nothing.

#### Scenario: Deleting an existing journey

- **WHEN** the fan has a journey for the event and Delete is called
- **THEN** the fan no longer has a journey for the event

#### Scenario: Deleting a journey that does not exist

- **WHEN** the fan has no journey for the event and Delete is called
- **THEN** Delete succeeds and nothing changes

#### Scenario: Other journeys are kept

- **WHEN** the fan has journeys for two events and Delete is called for one of them
- **THEN** the journey for the other event is kept
