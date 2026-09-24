# LotterySalesPhase.Create

## Purpose

Stores a new LotterySalesPhase for an event and returns it as stored, not yet drawn.

## Requirements

### Requirement: Store a phase

Create SHALL store the phase without a drawn time and return it. It SHALL fail with FailedPrecondition when the event does not exist.

#### Scenario: Phase stored

- **WHEN** Create is called for an existing event
- **THEN** the phase is stored, returned, and not drawn

#### Scenario: Unknown event

- **WHEN** the event does not exist
- **THEN** Create fails with FailedPrecondition and stores nothing
