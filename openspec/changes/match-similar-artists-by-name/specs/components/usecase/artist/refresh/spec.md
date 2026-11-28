## ADDED Requirements

### Requirement: Refresh keeps the name keys
When Artist.GetArtist returns the artist, ArtistUseCase.Refresh SHALL, after adopting the name, set the artist's name keys with Artist.UpdateNameKeys to the returned name keys and the key of the artist's name, also when the name did not change. It SHALL fail with the error of Artist.UpdateNameKeys. When Artist.GetArtist fails, the name keys SHALL not change.

#### Scenario: Alias added in the catalog
- **WHEN** the catalog's name equals the current name and the catalog now lists a new alias
- **THEN** the artist is found by the new alias

#### Scenario: Catalog unavailable
- **WHEN** Artist.GetArtist fails with Unavailable
- **THEN** the name keys are unchanged

#### Scenario: Keys cannot be stored
- **WHEN** Artist.UpdateNameKeys fails with NotFound
- **THEN** Refresh fails with NotFound
