## ADDED Requirements

### Requirement: Refresh keeps the known names
When Artist.GetArtist returns the artist, ArtistUseCase.Refresh SHALL, after adopting the name, set the artist's known names with Artist.UpdateKnownNames, naming the MBID it looked up, to the returned known names and the artist's name, also when the name did not change. It SHALL fail with the error of Artist.UpdateKnownNames. When Artist.GetArtist fails, the known names SHALL not change.

#### Scenario: Alias added in the catalog
- **WHEN** the catalog's name equals the current name and the catalog now lists a new alias
- **THEN** the artist is found by the new alias

#### Scenario: Catalog unavailable
- **WHEN** Artist.GetArtist fails with Unavailable
- **THEN** the known names are unchanged

#### Scenario: Names cannot be stored
- **WHEN** Artist.UpdateKnownNames fails with NotFound
- **THEN** Refresh fails with NotFound

### Requirement: Refresh writes only to the MBID it read
ArtistUseCase.Refresh SHALL give Artist.UpdateName and Artist.UpdateActivityEnded the MBID it looked up, so a refresh that read an MBID replaced in the meantime changes nothing.

#### Scenario: MBID corrected during a refresh
- **WHEN** an admin corrects an artist's MBID after Refresh read the earlier MBID from the catalog and before Refresh writes
- **THEN** the artist keeps the corrected name and activity status, and Refresh succeeds

