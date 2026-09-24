# ArtistUseCase.GetOfficialSite

## Purpose

ArtistUseCase.GetOfficialSite returns the official website recorded for an artist.

## Requirements

### Requirement: GetOfficialSite returns the artist's official site
ArtistUseCase.GetOfficialSite SHALL return what Artist.GetOfficialSite returns for the artist id and SHALL return its error unchanged.

#### Scenario: Site recorded
- **WHEN** GetOfficialSite is called for an artist with an official site
- **THEN** that site is returned

#### Scenario: No site recorded
- **WHEN** GetOfficialSite is called for an artist without an official site
- **THEN** GetOfficialSite fails with NotFound
