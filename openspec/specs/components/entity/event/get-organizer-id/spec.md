# Event.GetOrganizerID

## Purpose

Event.GetOrganizerID resolves the Organizer that owns an Event via its Series, so entity operations that stamp a payout record's Organizer never need their own join.

## Requirements

### Requirement: Organizer via the event's series

GetOrganizerID SHALL return the id of the Organizer that owns the Series the Event belongs to. It SHALL fail with NotFound when no Event has the id, or when the Event's Series has no Organizer (a discovery-pipeline series).

#### Scenario: Organizer-authored event

- **WHEN** the Event belongs to a Series owned by an Organizer
- **THEN** it returns that Organizer's id

#### Scenario: Unknown event

- **WHEN** no Event has the id
- **THEN** it fails with NotFound

#### Scenario: Discovery-pipeline event

- **WHEN** the Event's Series has no Organizer
- **THEN** it fails with NotFound

