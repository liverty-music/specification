## MODIFIED Requirements

### Requirement: SetHype changes an existing Follow only

SetHype SHALL set the hype level of the fan's Follow of the artist to the given level, set by the fan, from any level to any other. When the Follow already has the given level and it was set by the fan, SetHype SHALL succeed, change nothing and announce nothing. When the Follow already has the given level but it was set by default or by inference, SetHype SHALL record it as set by the fan. When the fan does not follow the artist, SetHype SHALL fail with NotFound and store nothing.

#### Scenario: Change the level

- **WHEN** the fan follows the artist at Nearby set by default and SetHype is called with Away
- **THEN** the Follow's hype level is Away, set by the fan

#### Scenario: Same level again

- **WHEN** the Follow is at Home set by the fan and SetHype is called with Home
- **THEN** SetHype succeeds, the level stays Home and nothing is announced

#### Scenario: Fan picks the default level

- **WHEN** the Follow is at Nearby set by default and SetHype is called with Nearby
- **THEN** the Follow is at Nearby, set by the fan

#### Scenario: Artist not followed

- **WHEN** the fan does not follow the artist
- **THEN** SetHype fails with NotFound and no Follow is created

### Requirement: A changed hype level is announced with the change

When SetHype changes the level or who set it, it SHALL announce the Follow as changed, with its new level and who set it, together with the change: both are stored or neither is. When the announcement cannot be recorded, SetHype SHALL fail with Unavailable and the level and who set it SHALL stay as they were.

#### Scenario: Level changed

- **WHEN** SetHype changes a Follow from Watch to Away
- **THEN** one hype change is announced, carrying the Follow at Away set by the fan

#### Scenario: Fan picks the default level

- **WHEN** SetHype records a Follow at Nearby set by default as Nearby set by the fan
- **THEN** one hype change is announced, carrying the Follow at Nearby set by the fan

#### Scenario: Announcement cannot be recorded

- **WHEN** SetHype changes a Follow from Watch to Away and the announcement cannot be recorded
- **THEN** SetHype fails with Unavailable and the Follow stays at Watch
