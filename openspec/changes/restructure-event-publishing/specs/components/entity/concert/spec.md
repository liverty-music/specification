# Spec Delta

## MODIFIED Requirements

### Requirement: A concert is exactly one event

A Concert SHALL be exactly one Event: it carries the Event's id, venue, listed venue name, date, times and publish state, and adds only the embedded Series and the performing Artists. A Concert SHALL have no title or source page of its own; they are read from its Series.

#### Scenario: Title comes from the series
- **WHEN** a Concert belongs to a Series titled "ARENA TOUR 2026"
- **THEN** the Concert's title is "ARENA TOUR 2026"

#### Scenario: Concert id is its event id
- **WHEN** a Concert extends the Event with id E
- **THEN** the Concert's id is E

#### Scenario: Cancelled date of a published tour
- **WHEN** a Concert extends a CANCELLED Event of a Series whose other Events are PUBLISHED
- **THEN** the Concert's publish state is CANCELLED

## ADDED Requirements

### Requirement: A draft event is not a concert

A DRAFT Event SHALL NOT be a Concert. No Concert operation SHALL return a DRAFT Event, match it against a discovered concert, merge into it, fill its times or remove it; an id of a DRAFT Event SHALL be treated by every Concert operation as an id that matches no Concert.

#### Scenario: Draft not returned by id
- **WHEN** Concert.ListByIDs is given the id of a DRAFT Event
- **THEN** that id is left out as unknown

#### Scenario: Discovery ignores a draft at the same slot
- **WHEN** discovery finds a concert at the Venue, date and start time of a DRAFT Event
- **THEN** the DRAFT Event is not found as an existing Event and is left unchanged

### Requirement: Fan visibility follows the event

A Concert SHALL be visible to fans exactly when its Event is publicly visible (see Event).

#### Scenario: Concert of an unlisted organizer series
- **WHEN** a Concert's Series is a first-party Series with visibility UNLISTED
- **THEN** the Concert is not visible to fans

#### Scenario: Cancelled date of a public series
- **WHEN** a Concert's Event is CANCELLED and its Series' other Events are PUBLISHED and PUBLIC
- **THEN** that Concert is not visible to fans

## REMOVED Requirements

### Requirement: Fan visibility follows the series

**Reason**: Visibility is decided per Event, so one date of a Series can be a draft or cancelled while the others are listed.
**Migration**: Replaced by "Fan visibility follows the event" above.
