# Artist.GetOfficialSite

## Purpose

Returns the official site of an artist.

## Requirements

### Requirement: GetOfficialSite returns the artist's site
GetOfficialSite SHALL return the official site stored for the given artist id and SHALL fail with NotFound when that artist has no official site, including when no artist has the id.

#### Scenario: Artist with a site
- **WHEN** GetOfficialSite is called for an artist that has an official site
- **THEN** it returns that site

#### Scenario: Artist without a site
- **WHEN** GetOfficialSite is called for an artist that has no official site
- **THEN** GetOfficialSite fails with NotFound
