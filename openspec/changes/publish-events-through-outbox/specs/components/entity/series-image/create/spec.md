## MODIFIED Requirements

### Requirement: Idempotent insert

Create SHALL store a SeriesImage with the Series it was uploaded for, and announce it as uploaded together with it: both are stored or neither is. When a SeriesImage with the same id is already stored, Create SHALL succeed, change nothing and announce nothing. When the announcement cannot be recorded, Create SHALL fail with Unavailable and store nothing.

#### Scenario: First attach

- **WHEN** Create is called with a SeriesImage that is not stored, for Series S
- **THEN** the SeriesImage is stored with Series S and announced as uploaded once

#### Scenario: Repeated attach
- **WHEN** the same SeriesImage id is inserted twice
- **THEN** one SeriesImage is stored, both calls succeed and it is announced once

#### Scenario: Announcement cannot be recorded

- **WHEN** Create is called with a SeriesImage that is not stored and the announcement cannot be recorded
- **THEN** Create fails with Unavailable and no SeriesImage is stored
