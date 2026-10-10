# Spec Delta

## MODIFIED Requirements

### Requirement: Whole catalog, oldest first

List SHALL return every Concert in the catalog — past and upcoming, of every Series whatever its visibility, and CANCELLED ones included — ordered by local date ascending, each with its Venue, Series, performers and publish state. StagedConcerts and DRAFT Events are not Concerts and SHALL NOT be returned. An empty catalog SHALL yield an empty list.

#### Scenario: Cancelled organizer concert included
- **WHEN** the catalog holds a CANCELLED Event of a first-party Series
- **THEN** List returns it as a CANCELLED Concert

#### Scenario: Staged concert excluded
- **WHEN** a StagedConcert is pending review
- **THEN** List does not return it

#### Scenario: Empty catalog
- **WHEN** the catalog holds no Concert
- **THEN** List returns an empty list

#### Scenario: Draft event excluded
- **WHEN** a published Series has a DRAFT Event
- **THEN** List does not return the DRAFT Event
