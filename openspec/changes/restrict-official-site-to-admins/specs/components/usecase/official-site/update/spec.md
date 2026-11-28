## ADDED Requirements

### Requirement: Update replaces the URL of the artist's official site

OfficialSiteUseCase.Update SHALL take an artist id and a URL, replace the URL of the artist's stored official site through Artist.UpdateOfficialSiteURL, and return the error of Artist.UpdateOfficialSiteURL unchanged.

#### Scenario: Artist with a site

- **WHEN** Update is called for an artist whose site is a wrong URL, with the right URL
- **THEN** the artist's official site is the right URL, with the id it had

#### Scenario: Artist without a site

- **WHEN** Update is called for an artist that has no official site
- **THEN** Update fails with NotFound and nothing is stored
