# List By Follower Grouped

## Purpose

ListByFollowerGrouped gives a User the Concerts of every Artist they follow, on or after a given date, grouped by date and sorted into HOME, NEARBY and AWAY relative to their home area, for their dashboard.

## Requirements

### Requirement: Followed artists' concerts in proximity groups

ListByFollowerGrouped SHALL read the Concerts of the User's followed Artists from the given date, or from the current date when none is given (Concert.ListByFollower), and return them as proximity groups relative to the User's home area (Concert.GroupByDateAndProximity), in date order. Concerts of first-party Series that are not publicly visible SHALL NOT be returned.

Known defect: liverty-music/backend#475

#### Scenario: Upcoming by default
- **WHEN** no date is given
- **THEN** only Concerts from the current date onward are grouped

#### Scenario: From a past date
- **WHEN** the given date is 7 days ago
- **THEN** Concerts from 7 days ago onward are grouped, with the same grouping and order

#### Scenario: No home area
- **WHEN** the User has no home area
- **THEN** every Concert is in its group's away list

#### Scenario: Follows nothing
- **WHEN** the User follows no Artist
- **THEN** no groups are returned, without error

#### Scenario: Cancelled organizer concert
- **WHEN** a followed Artist performs in a CANCELLED first-party Series
- **THEN** that Concert is not in any group
