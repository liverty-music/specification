# Series.GetAuthored

## Purpose

Returns a Series with its derived publish state and every one of its Events, whatever its publish state, each with its own publish state and its performers, as its Organizer authored them.

## Requirements

### Requirement: Every event with its publish state

GetAuthored SHALL return the Series with its cover image and its derived publish state, every Event of the Series whatever its publish state, each with its publish state, and the Artists performing at any of those Events. Events SHALL be ordered by date, then start time with unknown start times last. It SHALL fail with NotFound when no Series has the id.

#### Scenario: Draft series read
- **WHEN** a Series with two DRAFT Events is read
- **THEN** both Events are returned as DRAFT and the Series' publish state is DRAFT

#### Scenario: Published tour with a new date
- **WHEN** a Series with two PUBLISHED Events and one DRAFT Event is read
- **THEN** all three Events are returned, each with its own publish state

#### Scenario: Unknown series id
- **WHEN** no Series has the id
- **THEN** GetAuthored fails with NotFound
