# List

## Purpose

List gives an admin every ConcertCandidate awaiting review, oldest first, each with its performing Artist, its details as discovered and its resolved-venue preview.

## Requirements

### Requirement: Review queue with performers

List SHALL return every ConcertCandidate in review-queue order (ConcertCandidate.ListPending), each paired with its Artist. When any Artist cannot be read, List SHALL fail.

#### Scenario: Two pending concerts
- **WHEN** two ConcertCandidates are pending
- **THEN** both are returned, oldest first, each with its Artist

#### Scenario: Artist lookup fails
- **WHEN** the Artist of one ConcertCandidate cannot be read
- **THEN** List fails

#### Scenario: Empty queue
- **WHEN** nothing is pending
- **THEN** List returns an empty list
