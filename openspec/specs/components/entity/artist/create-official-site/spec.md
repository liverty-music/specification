# Artist.CreateOfficialSite

## Purpose

Stores the official site of an artist.

## Requirements

### Requirement: CreateOfficialSite stores one site per artist
CreateOfficialSite SHALL store the given official site with its id, artist_id and url. It SHALL fail with AlreadyExists when the artist already has an official site, with FailedPrecondition when no artist has the artist_id, and with InvalidArgument when the site's id is missing or malformed; in every failure nothing is stored.

#### Scenario: First site for an artist
- **WHEN** CreateOfficialSite is called for an artist without an official site
- **THEN** the site is stored and the artist's official site is that site

#### Scenario: Artist already has a site
- **WHEN** CreateOfficialSite is called for an artist that already has an official site
- **THEN** CreateOfficialSite fails with AlreadyExists and the existing site is kept

#### Scenario: Unknown artist
- **WHEN** CreateOfficialSite is called with an artist_id no artist has
- **THEN** CreateOfficialSite fails with FailedPrecondition and nothing is stored

#### Scenario: Site without an id
- **WHEN** CreateOfficialSite is called with a site that has no id
- **THEN** CreateOfficialSite fails with InvalidArgument and nothing is stored
