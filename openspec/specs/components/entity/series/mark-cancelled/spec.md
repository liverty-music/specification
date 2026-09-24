# Series.MarkCancelled

## Purpose

Moves a Series to CANCELLED and records when.

## Requirements

### Requirement: Mark cancelled

MarkCancelled SHALL set the Series' publish state to CANCELLED and its cancelled-at time to the given time, keeping its Events; it SHALL fail with NotFound when no Series has the id.

#### Scenario: Published series cancelled
- **WHEN** a PUBLISHED Series is marked cancelled
- **THEN** it is CANCELLED and its Events remain

#### Scenario: Unknown series
- **WHEN** no Series has the id
- **THEN** MarkCancelled fails with NotFound
