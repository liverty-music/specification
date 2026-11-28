## ADDED Requirements

### Requirement: CorrectMBID stores the chosen artist's names
ArtistUseCase.CorrectMBID SHALL give Artist.UpdateMBID the known names Artist.GetArtist returned for the chosen MBID.

#### Scenario: MBID chosen
- **WHEN** an admin corrects an artist to an MBID whose catalog artist has an alias
- **THEN** the artist is found by that alias
