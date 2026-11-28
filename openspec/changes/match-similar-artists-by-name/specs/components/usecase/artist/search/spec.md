## ADDED Requirements

### Requirement: Search registers a verified match with the catalog's names
ArtistUseCase.Search SHALL register a match it verified with the known names Artist.GetArtist returned for its MBID, and any other new match with the match's name as its only known name.

#### Scenario: Verified match
- **WHEN** a new match is verified and the catalog lists an alias for its MBID
- **THEN** the registered artist is found by that alias

#### Scenario: Ambiguous match
- **WHEN** a new match is ambiguous
- **THEN** it is registered with the match's name as its only known name
