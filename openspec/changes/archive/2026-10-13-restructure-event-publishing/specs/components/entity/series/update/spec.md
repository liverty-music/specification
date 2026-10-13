# Spec Delta

## Purpose

Applies an organizer's edit to a first-party Series in one step: its authored attributes, its DRAFT Events and performers, and the times of its PUBLISHED Events.

## ADDED Requirements

### Requirement: Apply the edit whole

Update SHALL take a Series, its title, type, source page, description and visibility, its performers, and a list of events, each with a Venue, a local date, an optional start time, an optional open time and, for an existing Event, that Event's id. Together or not at all, it SHALL:
- set the Series' title, type, source page, description and visibility, leaving its organizer and cover image unchanged;
- add each event given without an id as a new DRAFT Event whose Concert has the given performers;
- set the Venue, date and times of each given DRAFT Event, and make the given performers the performers of its Concert;
- remove each DRAFT Event of the Series that is not given;
- set the open time and start time of each given PUBLISHED Event and the performers of its Concert, leaving its Venue and date unchanged.

It SHALL fail with FailedPrecondition, changing nothing, when the Series does not exist or is not first-party, or when a given id is not an Event of the Series.

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

#### Scenario: Event of another series
- **WHEN** a given id belongs to an Event of another Series
- **THEN** Update fails with FailedPrecondition and nothing changes

### Requirement: A new start time takes its slot

When the start time of a given PUBLISHED Event changes, the Event SHALL take the slot at its Venue, date and new start time, keeping its id:
- when no Event that is not DRAFT is at that slot, the start time is simply set;
- when an Event of a discovered Series is at that slot, that Event SHALL be merged into this one: fans tracking it track this Event instead, its performers are added to this Event's Concert, and it is removed;
- when the slot is suppressed, or an Event of any other first-party Series is at that slot, Update SHALL fail with FailedPrecondition and change nothing.

#### Scenario: Start time announced
- **WHEN** a PUBLISHED Event with no start time is given the start time 18:00 and no Event is at that slot
- **THEN** the Event starts at 18:00 and keeps its id

#### Scenario: Discovered event at the new slot
- **WHEN** a PUBLISHED Event E is given 18:00 and a discovered Event D that fans track is at E's Venue and date at 18:00
- **THEN** E starts at 18:00 with its id kept, those fans track E, and D is gone

#### Scenario: Suppressed new slot
- **WHEN** the new slot of a PUBLISHED Event matches a SuppressedConcert
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: First-party event at the new slot
- **WHEN** the new slot of a PUBLISHED Event holds an Event of another first-party Series
- **THEN** Update fails with FailedPrecondition and nothing changes
