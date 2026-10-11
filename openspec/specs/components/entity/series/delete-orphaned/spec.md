# Series.DeleteOrphaned

## Purpose

Removes, from a given set of Series, those left with no Event and no pending ConcertCandidate.

## Requirements

### Requirement: Remove only empty candidates

DeleteOrphaned SHALL remove each given Series that has no Event and no ConcertCandidate, SHALL leave every other Series — given or not — unchanged, and SHALL return how many it removed. An empty set SHALL remove nothing. Repeating it SHALL remove nothing more.

#### Scenario: Empty series removed
- **WHEN** a given Series has no Event and no ConcertCandidate
- **THEN** it is removed

#### Scenario: Series with a concert candidate kept
- **WHEN** a given Series has no Event but one ConcertCandidate
- **THEN** it is kept

#### Scenario: Series not given
- **WHEN** an empty Series was not among those given
- **THEN** it is kept
