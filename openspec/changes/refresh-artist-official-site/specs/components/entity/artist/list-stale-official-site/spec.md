# Spec Delta

## Purpose

Returns the followed artists whose official site is due for a check in the music catalog: never checked, or last checked longer ago than a given age.

## ADDED Requirements

### Requirement: ListStaleOfficialSite returns due followed artists, never-checked first
ListStaleOfficialSite SHALL return, with their id, name and MBID, the artists that at least one fan follows and that have no official_site_check_time or an official_site_check_time older than the given age, whether or not they have an official site. It SHALL return never-checked artists first and then the oldest check first, each artist at most once, and at most the given number of artists. An artist nobody follows, or one checked within the given age, SHALL NOT be returned.

#### Scenario: Never-checked and stale artists
- **WHEN** one followed artist was never checked and another was last checked 8 days ago, and the age is 7 days
- **THEN** both are returned, the never-checked artist first

#### Scenario: Recently checked artist
- **WHEN** a followed artist was checked 2 days ago and the age is 7 days
- **THEN** the artist is not returned

#### Scenario: Followed artist without an official site
- **WHEN** a followed artist has no official site and was never checked
- **THEN** the artist is returned

#### Scenario: Artist nobody follows
- **WHEN** an artist was never checked and nobody follows it
- **THEN** the artist is not returned

#### Scenario: More due artists than the limit
- **WHEN** 30 followed artists are due and the limit is 20
- **THEN** 20 artists are returned

#### Scenario: Nothing due
- **WHEN** every followed artist was checked within the given age
- **THEN** an empty list is returned without error
