# StagedConcert.ListPending

## Purpose

Lists every StagedConcert awaiting review in review-queue order.

## Requirements

### Requirement: Oldest first

ListPending SHALL return every StagedConcert ordered by discovered time ascending; an empty queue SHALL yield an empty list.

#### Scenario: Two staged concerts
- **WHEN** one StagedConcert was staged yesterday and one today
- **THEN** yesterday's is returned first

#### Scenario: Empty queue
- **WHEN** nothing is staged
- **THEN** ListPending returns an empty list
