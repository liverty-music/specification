## ADDED Requirements

### Requirement: A removed Follow is announced with the change

When Unfollow removes a Follow, it SHALL announce the Follow as removed, carrying the Follow as it was, together with the removal: both are stored or neither is. When the fan does not follow the artist, Unfollow SHALL announce nothing. When the announcement cannot be recorded, Unfollow SHALL fail with Unavailable and the Follow SHALL remain.

#### Scenario: Followed artist unfollowed

- **WHEN** the fan follows the artist at Away and Unfollow is called
- **THEN** one unfollow is announced, carrying the Follow at Away

#### Scenario: Artist not followed

- **WHEN** the fan does not follow the artist and Unfollow is called
- **THEN** Unfollow succeeds and nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** the fan follows the artist and the announcement of the unfollow cannot be recorded
- **THEN** Unfollow fails with Unavailable and the Follow remains
