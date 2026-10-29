# components/entity/seat-type/list-by-series Specification

## Purpose
Lists the SeatTypes of one Series, so a member can stock the Series' events with them.

## Requirements

### Requirement: Seat types of a series

ListBySeries SHALL return every SeatType of the given Series, highest price first, then by name, and an empty list when the Series has none or does not exist.

#### Scenario: Three seat types
- **WHEN** a Series has S席 at 9000 yen, A席 at 7000 yen and B席 at 7000 yen
- **THEN** S席, A席 and B席 are returned in that order

#### Scenario: No seat type
- **WHEN** the Series has no SeatType
- **THEN** an empty list is returned
