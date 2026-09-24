# Delete

## Purpose

Removes a fan's ticket journey for one event at the fan's request, so the event goes back to having no status for them.

## Requirements

### Requirement: Delete removes the fan's journey for the event

When a fan removes their journey for an event, Delete SHALL remove it through TicketJourney.Delete; removing a journey that does not exist therefore succeeds. When the removal fails, Delete SHALL fail with that error. Delete sends no status-change signal.

#### Scenario: The fan removes their journey

- **WHEN** the fan has a journey for the event and removes it
- **THEN** the fan no longer has a journey for the event

#### Scenario: Nothing to remove

- **WHEN** the fan has no journey for the event and removes it
- **THEN** Delete succeeds

#### Scenario: Removal fails

- **WHEN** TicketJourney.Delete fails
- **THEN** Delete fails with that error
