# components/usecase/artist/get Specification

## Purpose
ArtistUseCase.Get returns one Artist by its id, so the admin console can show an Artist it opens by id.

## Requirements

### Requirement: One artist by id

Get SHALL return the result of Artist.Get for the given id unchanged, and SHALL return its NotFound and InvalidArgument unchanged.

#### Scenario: Known artist
- **WHEN** Get is called with the id of a registered Artist
- **THEN** that Artist is returned

#### Scenario: Unknown artist
- **WHEN** Get is called with an id no Artist has
- **THEN** it fails with NotFound
