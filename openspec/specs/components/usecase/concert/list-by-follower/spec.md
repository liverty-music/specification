# List By Follower

## Purpose

ListByFollower returns, ungrouped, the Concerts of every Artist a User follows on or after a given date, oldest first.

## Requirements

### Requirement: Followed artists' concerts

ListByFollower SHALL return the result of Concert.ListByFollower for the User and date unchanged, the current date being used when no date is given.

#### Scenario: Default date
- **WHEN** no date is given
- **THEN** the followed Artists' Concerts from the current date onward are returned, oldest first

#### Scenario: Follows nothing
- **WHEN** the User follows no Artist
- **THEN** an empty list is returned
