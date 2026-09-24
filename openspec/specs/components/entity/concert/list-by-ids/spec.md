# Concert.ListByIDs

## Purpose

Returns the Concerts with the given ids, each with its Venue including coordinates, Series and performers, regardless of fan visibility.

## Requirements

### Requirement: Concerts by id

ListByIDs SHALL return the Concert for each given id that exists, ordered by local date ascending, each with its Venue with coordinates when known, Series and performers. Ids that match no Concert SHALL be left out without error. The Series' visibility SHALL NOT filter the result.

#### Scenario: One unknown id
- **WHEN** ListByIDs is given two existing ids and one unknown id
- **THEN** it returns the two Concerts

#### Scenario: Empty id list
- **WHEN** ListByIDs is given no ids
- **THEN** it fails with InvalidArgument
