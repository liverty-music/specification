# ArtistNameResolutionUseCase.ResolveCanonicalName

## Purpose

ArtistNameResolutionUseCase.ResolveCanonicalName replaces a newly registered artist's name with the music catalog's canonical name for its MBID, so every artist shows the name the catalog uses.

## Requirements

### Requirement: ResolveCanonicalName adopts the catalog's name
ArtistNameResolutionUseCase.ResolveCanonicalName SHALL take an artist id, MBID and the artist's current name, look the MBID up with Artist.GetArtist and, when the catalog's name is not empty and differs from the current name, set it with Artist.UpdateName. When the catalog's name is empty or equal to the current name, nothing SHALL change.

#### Scenario: Catalog name differs
- **WHEN** the current name is "the band" and the catalog's name is "The Band"
- **THEN** the artist's name becomes "The Band"

#### Scenario: Catalog name equal
- **WHEN** the catalog's name equals the current name
- **THEN** the name is not updated

#### Scenario: Catalog name empty
- **WHEN** the catalog returns an empty name
- **THEN** the name is not updated and ResolveCanonicalName does not fail

### Requirement: ResolveCanonicalName reports failures
ArtistNameResolutionUseCase.ResolveCanonicalName SHALL fail with the error of Artist.GetArtist without changing the name, and SHALL fail with the error of Artist.UpdateName.

#### Scenario: Catalog unavailable
- **WHEN** Artist.GetArtist fails with Unavailable
- **THEN** ResolveCanonicalName fails and the name is unchanged

#### Scenario: Artist gone
- **WHEN** Artist.UpdateName fails with NotFound
- **THEN** ResolveCanonicalName fails with NotFound

### Requirement: ResolveCanonicalName runs when an artist is newly registered
When an artist-created announcement is made, ResolveCanonicalName SHALL run with the announced artist id, MBID and name. When the run fails, it SHALL be retried up to 3 more times.

#### Scenario: Artist announced
- **WHEN** an artist-created announcement is made for an artist
- **THEN** ResolveCanonicalName runs with that artist's id, MBID and announced name
