## ADDED Requirements

### Requirement: Create registers the catalog's names
When Artist.GetArtist succeeds, ArtistUseCase.Create SHALL register the artist with the returned name keys; when it fails, with the key of the given name only.

#### Scenario: Catalog lists aliases
- **WHEN** Create is called and the catalog lists an alias for the MBID
- **THEN** the registered artist is found by that alias

#### Scenario: Catalog lookup fails
- **WHEN** Artist.GetArtist fails with Unavailable
- **THEN** the artist is registered with the key of the given name
