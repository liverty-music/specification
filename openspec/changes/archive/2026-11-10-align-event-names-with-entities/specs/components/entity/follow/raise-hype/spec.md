## MODIFIED Requirements

### Requirement: A raised hype level is announced with the change

When RaiseHype changes the level, it SHALL announce the Follow's hype as changed (Follow.HypeChanged), with its new level and who set it (inference), together with the change: both are stored or neither is. When it changes nothing, it SHALL announce nothing. When the announcement cannot be recorded, RaiseHype SHALL fail with Unavailable and the Follow SHALL stay as it was.

#### Scenario: Level raised

- **WHEN** RaiseHype raises a Follow from Nearby to Away
- **THEN** one hype change is announced, carrying the Follow at Away set by inference

#### Scenario: Announcement cannot be recorded

- **WHEN** RaiseHype would raise a Follow from Nearby to Away and the announcement cannot be recorded
- **THEN** RaiseHype fails with Unavailable and the Follow stays at Nearby set by default
