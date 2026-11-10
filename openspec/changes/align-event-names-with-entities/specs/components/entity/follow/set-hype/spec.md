## MODIFIED Requirements

### Requirement: A changed hype level is announced with the change

When SetHype changes the level or who set it, it SHALL announce the Follow's hype as changed (Follow.HypeChanged), with its new level and who set it, together with the change: both are stored or neither is. When the announcement cannot be recorded, SetHype SHALL fail with Unavailable and the level and who set it SHALL stay as they were.

#### Scenario: Level changed

- **WHEN** SetHype changes a Follow from Watch to Away
- **THEN** one hype change is announced, carrying the Follow at Away set by the fan

#### Scenario: Fan picks the default level

- **WHEN** SetHype records a Follow at Nearby set by default as Nearby set by the fan
- **THEN** one hype change is announced, carrying the Follow at Nearby set by the fan

#### Scenario: Announcement cannot be recorded

- **WHEN** SetHype changes a Follow from Watch to Away and the announcement cannot be recorded
- **THEN** SetHype fails with Unavailable and the Follow stays at Watch
