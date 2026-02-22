## ADDED Requirements

### Requirement: List Followers of an Artist

The `ArtistRepository` SHALL provide a `ListFollowers` method that returns all users who follow a specific artist.

#### Scenario: Artist has multiple followers

- **WHEN** `ListFollowers` is called with an artist ID that has multiple followers
- **THEN** it SHALL return a slice of `User` entities for all users following that artist

#### Scenario: Artist has no followers

- **WHEN** `ListFollowers` is called with an artist ID that has no followers
- **THEN** it SHALL return an empty slice without error

#### Scenario: Artist does not exist

- **WHEN** `ListFollowers` is called with a non-existent artist ID
- **THEN** it SHALL return an empty slice without error
