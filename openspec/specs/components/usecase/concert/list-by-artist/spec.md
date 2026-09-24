# List By Artist

## Purpose

ListByArtist returns every Concert in which the given Artist performs — past and upcoming, oldest first — each with its Venue, Series, listed venue name and performers. Concerts of first-party Series that are not publicly visible are left out.

## Requirements

### Requirement: All of an artist's visible concerts

ListByArtist SHALL return the Artist's Concerts of every date (Concert.ListByArtist, not limited to upcoming). An Artist with no Concerts, and an Artist that does not exist, SHALL yield an empty list, not an error.

#### Scenario: Past concerts included
- **WHEN** the Artist performed last month and performs next month
- **THEN** both Concerts are returned, last month's first

#### Scenario: No concerts
- **WHEN** the Artist has no Concert
- **THEN** an empty list is returned

#### Scenario: Unknown artist
- **WHEN** no Artist has the given id
- **THEN** an empty list is returned

#### Scenario: Missing artist
- **WHEN** no Artist id is given
- **THEN** ListByArtist fails with InvalidArgument
