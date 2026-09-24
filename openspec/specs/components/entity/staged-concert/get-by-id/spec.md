# StagedConcert.GetByID

## Purpose

Returns one StagedConcert by id.

## Requirements

### Requirement: Get by id

GetByID SHALL return the StagedConcert with the given id and SHALL fail with NotFound when none exists, including after it was approved or rejected.

#### Scenario: Already approved
- **WHEN** the StagedConcert was approved and removed
- **THEN** GetByID fails with NotFound
