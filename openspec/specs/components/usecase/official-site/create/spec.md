# OfficialSiteUseCase.Create

## Purpose

OfficialSiteUseCase.Create records the official website of an artist, so concert discovery for that artist can use it. An artist has at most one official site.

## Requirements

### Requirement: Create stores a new official site for the artist
OfficialSiteUseCase.Create SHALL take an artist id and a URL, store them as a new OfficialSite with a fresh id through Artist.CreateOfficialSite, and return the error of Artist.CreateOfficialSite unchanged.

#### Scenario: Artist without a site
- **WHEN** Create is called for an artist that has no official site
- **THEN** the artist's official site is the given URL, with a fresh id

#### Scenario: Artist already has a site
- **WHEN** Create is called for an artist that already has an official site
- **THEN** Create fails with AlreadyExists and the existing site is kept

#### Scenario: Unknown artist
- **WHEN** Create is called with an artist id no artist has
- **THEN** Create fails with FailedPrecondition
