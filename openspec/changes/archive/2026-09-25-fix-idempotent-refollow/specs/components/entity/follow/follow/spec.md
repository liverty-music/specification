# Spec Delta

## MODIFIED Requirements

### Requirement: Follow creates at most one Follow per fan and artist

Follow SHALL store a Follow for the fan and the artist at hype level Nearby. When the fan already follows the artist, Follow SHALL fail with AlreadyExists and leave the existing Follow and its hype level unchanged. When the fan or the artist does not exist, Follow SHALL fail with FailedPrecondition and store nothing.

#### Scenario: First follow

- **WHEN** the fan does not follow the artist
- **THEN** a Follow at hype level Nearby is stored

#### Scenario: Repeat follow

- **WHEN** the fan already follows the artist at hype level Away
- **THEN** Follow fails with AlreadyExists and the Follow stays at Away

#### Scenario: Unknown artist

- **WHEN** the artist does not exist
- **THEN** Follow fails with FailedPrecondition and nothing is stored
