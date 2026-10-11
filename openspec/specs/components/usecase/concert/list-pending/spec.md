# List Pending

## Purpose

ListPending gives an admin every ConcertCandidate awaiting review, oldest first, each with its performing Artist, its details as discovered and its resolved-venue preview.

## Requirements

### Requirement: Review queue with performers

ListPending SHALL return every ConcertCandidate in review-queue order (ConcertCandidate.ListPending), each paired with its Artist. When any Artist cannot be read, ListPending SHALL fail.

#### Scenario: Two pending concerts
- **WHEN** two ConcertCandidates are pending
- **THEN** both are returned, oldest first, each with its Artist

#### Scenario: Artist lookup fails
- **WHEN** the Artist of one ConcertCandidate cannot be read
- **THEN** ListPending fails

#### Scenario: Empty queue
- **WHEN** nothing is pending
- **THEN** ListPending returns an empty list
