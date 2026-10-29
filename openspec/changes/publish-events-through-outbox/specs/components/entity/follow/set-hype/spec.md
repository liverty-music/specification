## MODIFIED Requirements

### Requirement: SetHype changes an existing Follow only

SetHype SHALL set the hype level of the fan's Follow of the artist to the given level, from any level to any other. When the Follow already has the given level, SetHype SHALL succeed, change nothing and announce nothing. When the fan does not follow the artist, SetHype SHALL fail with NotFound and store nothing.

#### Scenario: Change the level

- **WHEN** the fan follows the artist at Nearby and SetHype is called with Away
- **THEN** the Follow's hype level is Away

#### Scenario: Same level again

- **WHEN** the Follow is at Home and SetHype is called with Home
- **THEN** SetHype succeeds, the level stays Home and nothing is announced

#### Scenario: Artist not followed

- **WHEN** the fan does not follow the artist
- **THEN** SetHype fails with NotFound and no Follow is created

## ADDED Requirements

### Requirement: A changed hype level is announced with the change

When SetHype changes the level, it SHALL announce the Follow as changed, with its new level, together with the change: both are stored or neither is. When the announcement cannot be recorded, SetHype SHALL fail with Unavailable and the level SHALL stay as it was.

#### Scenario: Level changed

- **WHEN** SetHype changes a Follow from Watch to Away
- **THEN** one hype change is announced, carrying the Follow at Away

#### Scenario: Announcement cannot be recorded

- **WHEN** SetHype changes a Follow from Watch to Away and the announcement cannot be recorded
- **THEN** SetHype fails with Unavailable and the Follow stays at Watch
