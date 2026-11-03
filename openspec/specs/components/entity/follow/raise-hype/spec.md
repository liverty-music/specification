# components/entity/follow/raise-hype Specification

## Purpose
Raises the hype level of an existing Follow to a given level on the app's behalf, only when the Follow is raisable to it, and says whether it changed.

## Requirements

### Requirement: RaiseHype changes only a raisable Follow

RaiseHype SHALL set the fan's Follow of the artist to the given level, set by inference, and report that it changed, only when the Follow is raisable to that level at the moment of the write. Otherwise it SHALL leave the Follow unchanged and report that nothing changed. The check and the write SHALL take effect together, so a level the fan stored first is never replaced by RaiseHype. When the fan does not follow the artist, RaiseHype SHALL fail with NotFound.

#### Scenario: Raisable Follow

- **WHEN** the Follow is at Nearby set by default and RaiseHype is called with Away
- **THEN** the Follow is at Away set by inference and RaiseHype reports a change

#### Scenario: Level the fan set

- **WHEN** the Follow is at Home set by the fan and RaiseHype is called with Away
- **THEN** the Follow stays at Home set by the fan and RaiseHype reports no change

#### Scenario: Fan sets the level at the same time

- **WHEN** the fan's SetHype to Home is stored just before a RaiseHype to Away for the same Follow
- **THEN** the Follow is at Home set by the fan

#### Scenario: Artist not followed

- **WHEN** the fan does not follow the artist
- **THEN** RaiseHype fails with NotFound

### Requirement: A raised hype level is announced with the change

When RaiseHype changes the level, it SHALL announce the Follow as changed, with its new level and who set it (inference), together with the change: both are stored or neither is. When it changes nothing, it SHALL announce nothing. When the announcement cannot be recorded, RaiseHype SHALL fail with Unavailable and the Follow SHALL stay as it was.

#### Scenario: Level raised

- **WHEN** RaiseHype raises a Follow from Nearby to Away
- **THEN** one hype change is announced, carrying the Follow at Away set by inference

#### Scenario: Announcement cannot be recorded

- **WHEN** RaiseHype would raise a Follow from Nearby to Away and the announcement cannot be recorded
- **THEN** RaiseHype fails with Unavailable and the Follow stays at Nearby set by default
