# SeriesImage.Create

## Purpose

Records an uploaded SeriesImage for its Organizer.

## Requirements

### Requirement: Idempotent insert

Create SHALL store the SeriesImage, and SHALL succeed without change when a SeriesImage with the same id is already stored.

#### Scenario: Repeated attach
- **WHEN** the same SeriesImage id is inserted twice
- **THEN** one SeriesImage is stored and both calls succeed
