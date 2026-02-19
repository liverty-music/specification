## ADDED Requirements

### Requirement: List All Followed Artists

The `ArtistRepository` SHALL provide a `ListAllFollowed` method that returns all distinct artists followed by any user in the system.

#### Scenario: Multiple users follow the same artist

- **WHEN** `ListAllFollowed` is called and multiple users follow the same artist
- **THEN** the artist SHALL appear only once in the result set

#### Scenario: No followed artists

- **WHEN** `ListAllFollowed` is called and no users follow any artists
- **THEN** it SHALL return an empty slice without error

#### Scenario: Mixed followed and unfollowed artists

- **WHEN** some artists in the system have followers and others do not
- **THEN** only artists with at least one follower SHALL be returned
