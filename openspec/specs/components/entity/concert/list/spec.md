# Concert.List

## Purpose

Returns the whole Concert catalog with no audience filter, each Concert with its Venue, Series and performers.

## Requirements

### Requirement: Whole catalog, oldest first

List SHALL return every Concert in the catalog — past and upcoming, of every Series whatever its visibility or publish state — ordered by local date ascending, each with its Venue, Series and performers. StagedConcerts and DraftEvents are not Concerts and SHALL NOT be returned. An empty catalog SHALL yield an empty list.

#### Scenario: Cancelled organizer concert included
- **WHEN** the catalog holds a Concert of a CANCELLED first-party Series
- **THEN** List returns it

#### Scenario: Staged concert excluded
- **WHEN** a StagedConcert is pending review
- **THEN** List does not return it

#### Scenario: Empty catalog
- **WHEN** the catalog holds no Concert
- **THEN** List returns an empty list
