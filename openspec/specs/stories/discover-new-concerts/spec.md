# Discover new concerts

## Purpose

An Artist's newly announced concerts reach the catalog without anyone entering them: a search finds them, and each is published, held for review, or skipped, depending on what the catalog already knows.

## Requirements

### Requirement: A found concert is published or held for review

When ConcertUseCase.SearchNewConcerts announces new concerts for an Artist, ConcertCreationUseCase.CreateFromDiscovered SHALL process that discovery, so that each new concert at a resolvable venue with a free slot becomes a Concert in the catalog, and each concert at an unresolvable venue or colliding slot becomes a StagedConcert.

#### Scenario: New tour announced
- **WHEN** a followed Artist announces a three-stop tour at known venues and the daily search runs
- **THEN** the three stops are Concerts of one TOUR Series in the catalog

#### Scenario: Unknown venue
- **WHEN** a found concert's venue cannot be resolved
- **THEN** it is a StagedConcert and not a Concert

### Requirement: Rediscovery changes nothing

A concert found again by a later search SHALL NOT be announced or stored a second time, and a start time announced later SHALL be filled onto the Artist's existing Concert.

#### Scenario: Same tour found next week
- **WHEN** the search runs again after the freshness window and the tour is unchanged
- **THEN** no new Concert, StagedConcert or Series exists

#### Scenario: Start time published later
- **WHEN** a stop first found without a start time is found again starting at 18:00
- **THEN** the existing Concert starts at 18:00 and no second Concert exists
