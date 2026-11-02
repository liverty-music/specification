## ADDED Requirements

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
