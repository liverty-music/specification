## MODIFIED Requirements

### Requirement: Overwrite the listed venue name only

UpdateEventListedVenueName SHALL set the Event's listed venue name to the given name, keep the name it replaces among the Event's other listed venue names, and SHALL NOT change its Venue, the Venue's place id, its Series or its times. Giving the name the Event already lists SHALL change nothing. An unknown Event id SHALL be a success that changes nothing.

#### Scenario: Name replaced
- **WHEN** an Event lists "Zepp" and "Zepp DiverCity" is given
- **THEN** the Event lists "Zepp DiverCity", is still listed under "Zepp", and its Venue is unchanged

#### Scenario: Repeated update
- **WHEN** an Event lists "Zepp DiverCity" and "Zepp DiverCity" is given again
- **THEN** nothing changes

#### Scenario: Unknown event
- **WHEN** the Event id does not exist
- **THEN** the call succeeds and nothing changes
