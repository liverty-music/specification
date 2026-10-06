# Artist.UpdateOfficialSiteURL

## Purpose

Replaces the address of an artist's stored official site, keeping the site's identity.

## Requirements

### Requirement: UpdateOfficialSiteURL replaces the stored URL
UpdateOfficialSiteURL SHALL replace the url of the official site stored for the given artist id with the given URL and keep the site's id and artist. It SHALL fail with NotFound when that artist has no official site, including when no artist has the id, and with InvalidArgument when the URL is not a valid official site URL; in every failure the stored site is unchanged.

#### Scenario: Artist with a site
- **WHEN** UpdateOfficialSiteURL is called for an artist whose site is `http://hitsujibungaku.jimdo.com/` with `https://www.hitsujibungaku.info/`
- **THEN** the artist's official site has the same id and the new URL

#### Scenario: Artist without a site
- **WHEN** UpdateOfficialSiteURL is called for an artist that has no official site
- **THEN** UpdateOfficialSiteURL fails with NotFound and nothing is stored

#### Scenario: Invalid URL
- **WHEN** UpdateOfficialSiteURL is called with a URL longer than 2048 characters
- **THEN** UpdateOfficialSiteURL fails with InvalidArgument and the stored site is unchanged
