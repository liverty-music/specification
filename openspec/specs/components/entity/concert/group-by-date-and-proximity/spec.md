# Concert.GroupByDateAndProximity

## Purpose

Sorts a date-ordered list of Concerts into proximity groups, one per calendar date, relative to a home area.

## Requirements

### Requirement: One group per date, in input order

GroupByDateAndProximity SHALL produce one proximity group per distinct local date, in the order each date first appears in the input, and SHALL place each Concert in the list matching its proximity to the home area. Grouping no Concerts SHALL yield no groups.

#### Scenario: Mixed proximity on one date
- **WHEN** three Concerts on 2026-03-15 are HOME, NEARBY and AWAY
- **THEN** one group for 2026-03-15 holds one Concert in each list

#### Scenario: Dates keep input order
- **WHEN** the input dates are March 15, March 17, March 16 in that order
- **THEN** the groups are March 15, March 17, March 16

#### Scenario: No home area
- **WHEN** there is no home area
- **THEN** every Concert is in its group's away list

#### Scenario: No concerts
- **WHEN** the input is empty
- **THEN** no groups are produced
