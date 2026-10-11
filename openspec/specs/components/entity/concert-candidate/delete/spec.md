# ConcertCandidate.Delete

## Purpose

Removes a ConcertCandidate from the review queue.

## Requirements

### Requirement: Idempotent delete

Delete SHALL remove the ConcertCandidate with the given id and SHALL succeed without change when none exists.

#### Scenario: Already gone
- **WHEN** the ConcertCandidate does not exist
- **THEN** Delete succeeds
