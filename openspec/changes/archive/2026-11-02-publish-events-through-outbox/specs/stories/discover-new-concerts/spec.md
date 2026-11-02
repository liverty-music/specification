## MODIFIED Requirements

### Requirement: A found concert is published or held for review

When ConcertUseCase.SearchNewConcerts finds new concerts for an Artist, it SHALL start ConcertCreationUseCase.CreateFromDiscovered for that discovery, so that each new concert at a resolvable venue with a free slot becomes a Concert in the catalog, and each concert at an unresolvable venue or colliding slot becomes a ConcertCandidate.

#### Scenario: New tour announced
- **WHEN** a followed Artist announces a three-stop tour at known venues and the daily search runs
- **THEN** the three stops are Concerts of one TOUR Series in the catalog

#### Scenario: Unknown venue
- **WHEN** a found concert's venue cannot be resolved
- **THEN** it is a ConcertCandidate and not a Concert
