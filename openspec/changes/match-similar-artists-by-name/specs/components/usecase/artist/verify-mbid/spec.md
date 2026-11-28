## ADDED Requirements

### Requirement: VerifyMBID stores the verified artist's names
For a verified MBID, ArtistUseCase.VerifyMBID SHALL give Artist.UpdateMBID the known names Artist.GetArtist returned for that MBID. An ambiguous result changes no name key.

#### Scenario: Namesake chosen
- **WHEN** the artist is verified with a namesake's MBID
- **THEN** it is found by that namesake's name and aliases

#### Scenario: Ambiguous
- **WHEN** the MBID is ambiguous
- **THEN** the artist's known names are unchanged
