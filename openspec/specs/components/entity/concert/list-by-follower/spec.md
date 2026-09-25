# Concert.ListByFollower

## Purpose

Lists the Concerts of every Artist a User follows from a given date onward, each with its Venue including coordinates, Series and performers.

## Requirements

### Requirement: Followed artists' concerts from a date

ListByFollower SHALL return, once each, every Concert at which at least one Artist the User follows performs and whose local date is on or after the given date, ordered by local date ascending. When no date is given, the current date SHALL be used. Each Concert SHALL carry its Venue with coordinates when known. Concerts of a Series that is not publicly visible SHALL be left out.

#### Scenario: Default start is today
- **WHEN** no date is given and a followed Artist has a concert yesterday and tomorrow
- **THEN** only tomorrow's Concert is returned

#### Scenario: Past start date widens the range
- **WHEN** the given date is 7 days ago
- **THEN** Concerts from 7 days ago onward are returned

#### Scenario: Two followed performers at one concert
- **WHEN** the User follows both performers of one Concert
- **THEN** that Concert is returned once

#### Scenario: Unlisted organizer concert excluded
- **WHEN** a followed Artist performs in a PUBLISHED UNLISTED first-party Series
- **THEN** that Concert is not returned

#### Scenario: Follows nothing
- **WHEN** the User follows no Artist
- **THEN** ListByFollower returns an empty list
