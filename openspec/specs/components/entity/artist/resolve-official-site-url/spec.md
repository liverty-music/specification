# Artist.ResolveOfficialSiteURL

## Purpose

Looks up, in the music catalog, the official homepage of the artist with a given MBID.

## Requirements

### Requirement: ResolveOfficialSiteURL picks the most relevant active homepage
Among the catalog's official-homepage links for the MBID that have not ended, ResolveOfficialSiteURL SHALL return the first link credited to the catalog's name for the artist (compared ignoring case); when there is none, the first uncredited link; otherwise the first link. When no official-homepage link is active, it SHALL return no URL and no error.

#### Scenario: Link credited to the artist's name
- **WHEN** the active links are one credited to another name, one uncredited, and one credited to the artist's name in different case
- **THEN** the link credited to the artist's name is returned

#### Scenario: Uncredited link
- **WHEN** the active links are one credited to another name and one uncredited
- **THEN** the uncredited link is returned

#### Scenario: Only other credits
- **WHEN** every active link is credited to another name
- **THEN** the first active link is returned

#### Scenario: All links ended
- **WHEN** every official-homepage link for the MBID has ended
- **THEN** no URL is returned and there is no error

#### Scenario: No homepage link
- **WHEN** the catalog has no official-homepage link for the MBID
- **THEN** no URL is returned and there is no error

### Requirement: ResolveOfficialSiteURL reports catalog failures
ResolveOfficialSiteURL SHALL fail with Unavailable when the catalog cannot be reached and with Internal for an unexpected catalog response.

#### Scenario: Catalog unreachable
- **WHEN** the catalog cannot be reached
- **THEN** ResolveOfficialSiteURL fails with Unavailable
