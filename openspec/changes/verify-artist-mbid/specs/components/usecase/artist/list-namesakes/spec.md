## Purpose

ArtistUseCase.ListNamesakes shows an admin the music catalog's artists that share a registered artist's name, each with the details that tell them apart, so the admin can choose which one the artist is.

## ADDED Requirements

### Requirement: ListNamesakes returns the artist's namesakes with their official sites
ArtistUseCase.ListNamesakes SHALL take an artist id, get the artist with Artist.Get, look its name up with Artist.ListNamesakes, and return those CatalogArtists in the catalog's order, each with its official_site_url read with Artist.ListOfficialSiteRelations and chosen with Artist.SelectOfficialSite. When the artist's own mbid is not among them, it SHALL be listed first with the name Artist.GetArtist returns for it and its official_site_url, without country, life span or disambiguation, so the admin always sees the current MBID among the choices.

#### Scenario: Two namesakes
- **WHEN** ListNamesakes is called for an artist whose name the catalog gives to a UK band (its mbid) and a Japanese band with an official homepage
- **THEN** both are returned, the Japanese band with its official_site_url and the UK band without one

#### Scenario: Current MBID not found by name
- **WHEN** the catalog's search by the artist's name does not return the artist's own mbid
- **THEN** the artist's mbid is listed first, followed by the namesakes

### Requirement: ListNamesakes reports failures
ArtistUseCase.ListNamesakes SHALL fail with NotFound when no artist has the id, and with the error of Artist.ListNamesakes, Artist.ListOfficialSiteRelations or Artist.GetArtist unchanged.

#### Scenario: Unknown artist
- **WHEN** no artist has the id
- **THEN** ListNamesakes fails with NotFound

#### Scenario: Catalog unavailable
- **WHEN** Artist.ListNamesakes fails with Unavailable
- **THEN** ListNamesakes fails with Unavailable
