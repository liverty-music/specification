# Spec Delta

## MODIFIED Requirements

### Requirement: Followed artists' concerts from a date

ListByFollower SHALL return, once each, every Concert at which at least one Artist the User follows performs and whose local date is on or after the given date, ordered by local date ascending. When no date is given, the current date SHALL be used. Each Concert SHALL carry its Venue with coordinates when known. Concerts that are not visible to fans (see Concert) SHALL be left out.

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
- **WHEN** a followed Artist performs at a PUBLISHED Event of an UNLISTED first-party Series
- **THEN** that Concert is not returned

#### Scenario: Follows nothing
- **WHEN** the User follows no Artist
- **THEN** ListByFollower returns an empty list

#### Scenario: Draft and cancelled dates of a published tour excluded
- **WHEN** a followed Artist performs in a PUBLIC Series with one PUBLISHED, one DRAFT and one CANCELLED Event, all upcoming
- **THEN** only the PUBLISHED Event's Concert is returned
