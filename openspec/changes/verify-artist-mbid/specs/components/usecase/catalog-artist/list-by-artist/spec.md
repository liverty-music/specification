## Purpose

CatalogArtistUseCase.ListByArtist shows an admin the music catalog's artists that share a registered artist's name, each with the details that tell them apart, so the admin can choose which one the artist is.

## ADDED Requirements

### Requirement: ListByArtist returns the artist's namesakes with their official sites
CatalogArtistUseCase.ListByArtist SHALL take an artist id, get the artist with Artist.Get, look its name up with Artist.ListNamesakes, and return those CatalogArtists in the catalog's order, each with its official_site_url read with Artist.ListOfficialSiteRelations and chosen with Artist.SelectOfficialSite (none when Artist.ListOfficialSiteRelations fails with NotFound, as for a namesake the catalog merged or deleted after its name search was indexed). When the artist's own mbid is not among them, it SHALL be listed first with the name and activity status Artist.GetArtist returns for it and its official_site_url (none when Artist.ListOfficialSiteRelations fails with NotFound), without country, begin, end or disambiguation, so the admin always sees the current MBID among the choices; when Artist.GetArtist fails with NotFound because the catalog no longer knows that MBID, it SHALL be listed with the artist's registered name and no official_site_url instead of failing.

#### Scenario: Two namesakes
- **WHEN** ListByArtist is called for an artist whose name the catalog gives to a UK band (its mbid) and a Japanese band with an official homepage
- **THEN** both are returned, the Japanese band with its official_site_url and the UK band without one

#### Scenario: Namesake unknown to the catalog
- **WHEN** Artist.ListOfficialSiteRelations fails with NotFound for one namesake
- **THEN** that namesake is listed without official_site_url and ListByArtist succeeds

#### Scenario: Current MBID not found by name
- **WHEN** the catalog's search by the artist's name does not return the artist's own mbid
- **THEN** the artist's mbid is listed first, followed by the namesakes

#### Scenario: Current MBID unknown to the catalog
- **WHEN** Artist.GetArtist fails with NotFound for the artist's own mbid
- **THEN** that MBID is listed first with the artist's registered name, followed by the namesakes, and ListByArtist succeeds

### Requirement: ListByArtist reports failures
CatalogArtistUseCase.ListByArtist SHALL fail with NotFound when no artist has the id, and with the error of Artist.ListNamesakes, Artist.ListOfficialSiteRelations or Artist.GetArtist other than the NotFound cases above, unchanged.

#### Scenario: Unknown artist
- **WHEN** no artist has the id
- **THEN** ListByArtist fails with NotFound

#### Scenario: Catalog unavailable
- **WHEN** Artist.ListNamesakes fails with Unavailable
- **THEN** ListByArtist fails with Unavailable
