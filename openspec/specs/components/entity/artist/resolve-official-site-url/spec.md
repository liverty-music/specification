# Artist.SelectOfficialSite and Artist.ListOfficialSiteRelations

## Purpose

Reads the official-homepage links the music catalog has for an artist's MBID and picks the artist's official homepage from them.

## Requirements

### Requirement: SelectOfficialSite picks the most relevant active homepage
The music catalog's official-homepage links for an MBID SHALL be read as they are (ListOfficialSiteRelations: the catalog's name for the artist and every official-homepage link, with its credit and whether it has ended), and SelectOfficialSite SHALL pick the official site among them. Among the links that have not ended, SelectOfficialSite SHALL consider only the links that point at a site's top page (a URL with no path other than `/`, no query and no fragment) when at least one such link exists, and all active links otherwise. Among the links it considers, it SHALL return the first link credited to the catalog's name for the artist (compared ignoring case); when there is none, the first uncredited link; otherwise the first link. When no official-homepage link is active, it SHALL return no URL.

#### Scenario: Top page preferred over a label page
- **WHEN** the active links are `https://columbia.jp/artist-info/04limitedsazabys/` listed first and `https://www.04limitedsazabys.com/` listed second, both uncredited
- **THEN** `https://www.04limitedsazabys.com/` is returned

#### Scenario: Several top pages
- **WHEN** the active links are two top pages and one deeper link, all uncredited
- **THEN** the first of the two top pages is returned

#### Scenario: No top page
- **WHEN** every active link has a path other than `/`, as for an artist listed only on label pages
- **THEN** the first uncredited link among them is returned

#### Scenario: Link credited to the artist's name
- **WHEN** the active links are top pages, one credited to another name, one uncredited, and one credited to the artist's name in different case
- **THEN** the link credited to the artist's name is returned

#### Scenario: Uncredited link
- **WHEN** the active links are top pages, one credited to another name and one uncredited
- **THEN** the uncredited link is returned

#### Scenario: Only other credits
- **WHEN** every active link is credited to another name
- **THEN** the first active link among those considered is returned

#### Scenario: All links ended
- **WHEN** every official-homepage link for the MBID has ended
- **THEN** no URL is returned

#### Scenario: No homepage link
- **WHEN** the catalog has no official-homepage link for the MBID, only links of other types
- **THEN** ListOfficialSiteRelations returns no link and there is no error, and no URL is returned

### Requirement: ListOfficialSiteRelations reports catalog failures
ListOfficialSiteRelations SHALL fail with NotFound when the catalog has no artist for the MBID, with Unavailable when the catalog cannot be reached, and with Internal for an unexpected catalog response.

#### Scenario: Catalog unreachable
- **WHEN** the catalog cannot be reached
- **THEN** ListOfficialSiteRelations fails with Unavailable

#### Scenario: MBID unknown to the catalog
- **WHEN** the catalog has no artist for the MBID, as for an MBID removed from the catalog or one the catalog never had
- **THEN** ListOfficialSiteRelations fails with NotFound
