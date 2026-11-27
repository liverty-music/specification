## ADDED Requirements

### Requirement: Listed under a name

An Event SHALL be listed under a venue name when its listed venue name or one of its other listed venue names is the same listed venue as that name (see Venue, "Same listed venue"). An Event with neither SHALL be listed under no name.

#### Scenario: Listed venue name

- **WHEN** an Event's listed venue name is "Zepp Haneda(TOKYO)"
- **THEN** it is listed under "ZEPP HANEDA (TOKYO)"

#### Scenario: Other listed venue name

- **WHEN** an Event's listed venue name is "京セラドーム大阪" and its other listed venue names hold "Kyocera Dome Osaka"
- **THEN** it is listed under "Kyocera Dome Osaka"

#### Scenario: Name of another venue

- **WHEN** an Event's listed venue name is "京セラドーム大阪" and it has no other listed venue names
- **THEN** it is not listed under "Kyocera Dome Osaka"
