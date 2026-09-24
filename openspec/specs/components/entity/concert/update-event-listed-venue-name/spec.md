# Concert.UpdateEventListedVenueName

## Purpose

Replaces the listed venue name shown for an existing Event, leaving its Venue and every other attribute unchanged.

## Requirements

### Requirement: Overwrite the listed venue name only

UpdateEventListedVenueName SHALL set the Event's listed venue name to the given name and SHALL NOT change its Venue, the Venue's place id, its Series or its times. An unknown Event id SHALL be a success that changes nothing.

#### Scenario: Name replaced
- **WHEN** an Event lists "Zepp" and "Zepp DiverCity" is given
- **THEN** the Event lists "Zepp DiverCity" and its Venue is unchanged

#### Scenario: Unknown event
- **WHEN** the Event id does not exist
- **THEN** the call succeeds and nothing changes
