# ConcertCandidate.GetByID

## Purpose

Returns one ConcertCandidate by id.

## Requirements

### Requirement: Get by id

GetByID SHALL return the ConcertCandidate with the given id and SHALL fail with NotFound when none exists, including after it was approved or rejected.

#### Scenario: Already approved
- **WHEN** the ConcertCandidate was approved and removed
- **THEN** GetByID fails with NotFound
