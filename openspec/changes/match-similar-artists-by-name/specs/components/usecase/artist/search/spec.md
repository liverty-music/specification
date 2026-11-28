## ADDED Requirements

### Requirement: Search registers a new match under its name
ArtistUseCase.Search SHALL register each new match with the match's name as its only known name. The music catalog's names are stored when ArtistUseCase.VerifyMBID verifies the registered artist.

#### Scenario: New match registered under its name
- **WHEN** Search registers a new match
- **THEN** the registered artist's only known name is the match's name
