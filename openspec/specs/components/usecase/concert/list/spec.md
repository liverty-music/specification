# List

## Purpose

List gives an admin the whole Concert catalog — every Concert regardless of follow, proximity, date or visibility, oldest first — each with its Event id and performers so the admin can act on it.

## Requirements

### Requirement: Whole catalog for admins

List SHALL return the result of Concert.List unchanged. StagedConcerts SHALL be returned only by ListPending.

#### Scenario: Catalog and queue both populated
- **WHEN** the catalog holds Concerts and StagedConcerts are pending
- **THEN** List returns only the Concerts

#### Scenario: Unlisted organizer concert
- **WHEN** a Concert belongs to a PUBLISHED UNLISTED first-party Series
- **THEN** List returns it
