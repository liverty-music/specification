# StagedConcert.Delete

## Purpose

Removes a StagedConcert from the review queue.

## Requirements

### Requirement: Idempotent delete

Delete SHALL remove the StagedConcert with the given id and SHALL succeed without change when none exists.

#### Scenario: Already gone
- **WHEN** the StagedConcert does not exist
- **THEN** Delete succeeds
