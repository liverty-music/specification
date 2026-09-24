# ArtistUseCase.Create

## Purpose

ArtistUseCase.Create registers an artist from a name and an MBID, adopting the music catalog's canonical name when the catalog knows the MBID. Registering an MBID that is already known returns the existing artist.

## Requirements

### Requirement: Create registers the artist under the catalog's canonical name
ArtistUseCase.Create SHALL take an artist with a name and an MBID, look the MBID up with Artist.GetArtist and, when the catalog's name differs from the given name, register the artist with the catalog's name and MBID; otherwise with the given name. When the lookup fails, Create SHALL register the artist with the given name and SHALL NOT fail. The artist is registered with Artist.Create, and Create returns the artist that Artist.Create returns for it, which is the already registered artist when the MBID is known.

#### Scenario: Catalog has a different name
- **WHEN** Create is called with the name "the band" and an MBID whose catalog name is "The Band"
- **THEN** the artist is registered and returned with the name "The Band"

#### Scenario: Catalog lookup fails
- **WHEN** Create is called and Artist.GetArtist fails with Unavailable
- **THEN** the artist is registered and returned with the given name

#### Scenario: MBID already registered
- **WHEN** Create is called with an MBID that is already registered
- **THEN** the already registered artist is returned and no second artist is registered

### Requirement: Create reports registration failures
ArtistUseCase.Create SHALL return the error of Artist.Create unchanged, and SHALL fail with Internal when Artist.Create returns no artist. Create does not announce the new artist, so its images and canonical-name check wait for the daily image run.

#### Scenario: Registration rejected
- **WHEN** Artist.Create fails with InvalidArgument
- **THEN** Create fails with InvalidArgument

#### Scenario: Nothing returned
- **WHEN** Artist.Create returns no artist without an error
- **THEN** Create fails with Internal

#### Scenario: No announcement
- **WHEN** Create registers a new artist
- **THEN** no artist-created announcement is made
