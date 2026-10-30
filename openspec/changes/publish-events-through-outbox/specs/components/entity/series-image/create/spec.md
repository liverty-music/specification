## MODIFIED Requirements

### Requirement: Idempotent insert

Create SHALL store a SeriesImage for the Series it is attached to, and record the request to process it for that Series together with it: both are stored or neither is. The Series SHALL NOT be stored on the SeriesImage. When a SeriesImage with the same id is already stored, Create SHALL succeed, change nothing and record nothing. When the request cannot be recorded, Create SHALL fail with Unavailable and store nothing.

#### Scenario: First attach

- **WHEN** Create is called with a SeriesImage that is not stored, for Series S
- **THEN** the SeriesImage is stored and one request to process it for Series S is recorded

#### Scenario: Repeated attach
- **WHEN** the same SeriesImage id is inserted twice
- **THEN** one SeriesImage is stored, both calls succeed and one processing request is recorded

#### Scenario: Request cannot be recorded

- **WHEN** Create is called with a SeriesImage that is not stored and the processing request cannot be recorded
- **THEN** Create fails with Unavailable and no SeriesImage is stored
