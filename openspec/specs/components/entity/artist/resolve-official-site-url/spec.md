# Artist.ResolveOfficialSiteURL

## Purpose

Looks up, in the music catalog, the official homepage of the artist with a given MBID.

## Requirements

### Requirement: ResolveOfficialSiteURL picks the most relevant active homepage
Among the catalog's official-homepage links for the MBID that have not ended, ResolveOfficialSiteURL SHALL consider only the links that point at a site's top page (a URL with no path other than `/`, no query and no fragment) when at least one such link exists, and all active links otherwise. Among the links it considers, it SHALL return the first link credited to the catalog's name for the artist (compared ignoring case); when there is none, the first uncredited link; otherwise the first link. When no official-homepage link is active, it SHALL return no URL and no error.

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
- **THEN** no URL is returned and there is no error

#### Scenario: No homepage link
- **WHEN** the catalog has no official-homepage link for the MBID
- **THEN** no URL is returned and there is no error

### Requirement: ResolveOfficialSiteURL reports catalog failures
ResolveOfficialSiteURL SHALL fail with NotFound when the catalog has no artist for the MBID, with Unavailable when the catalog cannot be reached, and with Internal for an unexpected catalog response.

#### Scenario: Catalog unreachable
- **WHEN** the catalog cannot be reached
- **THEN** ResolveOfficialSiteURL fails with Unavailable

#### Scenario: MBID unknown to the catalog
- **WHEN** the catalog has no artist for the MBID, as for an MBID removed from the catalog or one the catalog never had
- **THEN** ResolveOfficialSiteURL fails with NotFound
