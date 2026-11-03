# Follow.Follow

## Purpose

Stores a new Follow of an artist by a fan, starting at hype level Nearby, and leaves an existing Follow for the same fan and artist untouched.

## Requirements

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

### Requirement: A new Follow is announced with the change

When Follow stores a new Follow, it SHALL announce the Follow as created, at hype level Nearby, together with the change: both are stored or neither is. When Follow fails, including with AlreadyExists, it SHALL announce nothing. When the announcement cannot be recorded, Follow SHALL fail with Unavailable and store no Follow.

#### Scenario: First follow announced

- **WHEN** the fan does not follow the artist and Follow is called
- **THEN** one follow is announced, carrying the Follow at Nearby

#### Scenario: Repeat follow

- **WHEN** the fan already follows the artist and Follow is called
- **THEN** Follow fails with AlreadyExists and nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** the fan does not follow the artist and the announcement cannot be recorded
- **THEN** Follow fails with Unavailable and the fan still does not follow the artist
