# Spec Delta

## MODIFIED Requirements

### Requirement: Apply the edit whole

Update SHALL take a Series, its title, type, source page, description and visibility, its performers, and a list of events, each with a Venue, a local date, an optional start time, an optional open time, an optional per-account limit and, for an existing Event, that Event's id. Together or not at all, it SHALL:
- set the Series' title, type, source page, description and visibility, leaving its Organizer and cover image unchanged;
- add each event given without an id as a new DRAFT Event whose Concert has the given performers, with the given per-account limit or 4;
- set the Venue, date, times and per-account limit of each given DRAFT Event, and make the given performers the performers of its Concert;
- remove each DRAFT Event of the Series that is not given;
- set the open time and start time of each given PUBLISHED Event and the performers of its Concert, leaving its Venue, date and per-account limit unchanged.

It SHALL fail with InvalidArgument, changing nothing, when a per-account limit breaks the Event rules, and with FailedPrecondition, changing nothing, when the Series does not exist or is not first-party, or when a given id is not an Event of the Series.

#### Scenario: Draft date removed
- **WHEN** a Series with two DRAFT Events is updated with only one of them
- **THEN** the Series has only that DRAFT Event

#### Scenario: Date added to a published tour
- **WHEN** a Series with one PUBLISHED Event is updated with that Event and a new event without an id
- **THEN** the new event is stored as a DRAFT Event whose Concert has the given performers, and the PUBLISHED Event keeps its Venue and date

#### Scenario: Doors-open time corrected
- **WHEN** a PUBLISHED Event is given with a new open time
- **THEN** its open time changes and its Venue and date do not

#### Scenario: Guest performer added after publish
- **WHEN** a PUBLISHED Event is given with one more performer
- **THEN** the performers of the Event's Concert include the added Artist, and its Venue and date do not change

#### Scenario: Draft limit changed
- **WHEN** a DRAFT Event with a per-account limit of 4 is given a limit of 2
- **THEN** its per-account limit is 2

#### Scenario: Published limit kept
- **WHEN** a PUBLISHED Event with a per-account limit of 4 is given a limit of 2
- **THEN** its per-account limit stays 4

#### Scenario: Event of another series
- **WHEN** a given id belongs to an Event of another Series
- **THEN** Update fails with FailedPrecondition and nothing changes
