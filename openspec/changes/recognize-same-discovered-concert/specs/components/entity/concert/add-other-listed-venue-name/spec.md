## Purpose

Records a listed venue name that an Event is also known by, so that a later discovery under that name is recognized as the same Event.

## ADDED Requirements

### Requirement: Add a name the event is also listed under

AddOtherListedVenueName SHALL add a normalized listed venue name to an Event's other listed venue names, leaving its listed venue name, Venue and every other attribute unchanged. It SHALL change nothing when the Event is already listed under that name (see Event, "Listed under a name"), and SHALL fail with NotFound when no Event that is not DRAFT has the given id.

#### Scenario: New name

- **WHEN** a name "Kyocera Dome Osaka" is added to an Event listed as "京セラドーム大阪"
- **THEN** the Event is listed under both names and its listed venue name is still "京セラドーム大阪"

#### Scenario: Name already known

- **WHEN** a name "KYOCERA DOME OSAKA" is added to an Event already listed under "Kyocera Dome Osaka"
- **THEN** nothing changes

#### Scenario: Unknown event

- **WHEN** the id matches no Event
- **THEN** AddOtherListedVenueName fails with NotFound
