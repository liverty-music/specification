# ConcertCandidate.ListPending

## Purpose

Lists every ConcertCandidate awaiting review in review-queue order.

## Requirements

### Requirement: Oldest first

ListPending SHALL return every ConcertCandidate ordered by discovered time ascending; an empty queue SHALL yield an empty list.

#### Scenario: Two concert candidates
- **WHEN** one ConcertCandidate was staged yesterday and one today
- **THEN** yesterday's is returned first

#### Scenario: Empty queue
- **WHEN** nothing is staged
- **THEN** ListPending returns an empty list
