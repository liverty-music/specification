## MODIFIED Requirements

### Requirement: Follow creates at most one Follow per fan and artist

Follow SHALL store a Follow for the fan and the artist at hype level Nearby, set by default. When the fan already follows the artist, Follow SHALL fail with AlreadyExists and leave the existing Follow, its hype level and who set it unchanged. When the fan or the artist does not exist, Follow SHALL fail with FailedPrecondition and store nothing.

#### Scenario: First follow

- **WHEN** the fan does not follow the artist
- **THEN** a Follow at hype level Nearby, set by default, is stored

#### Scenario: Repeat follow

- **WHEN** the fan already follows the artist at hype level Away set by the fan
- **THEN** Follow fails with AlreadyExists and the Follow stays at Away set by the fan

#### Scenario: Unknown artist

- **WHEN** the artist does not exist
- **THEN** Follow fails with FailedPrecondition and nothing is stored
