# Artist.MarkOfficialSiteChecked

## Purpose

Records when an artist's official site was last checked in the music catalog, whatever the check found.

## Requirements

### Requirement: MarkOfficialSiteChecked records the check time
MarkOfficialSiteChecked SHALL set the official_site_check_time of the artist with the given id to the given time, whether or not the artist has an official site, and SHALL fail with NotFound when no artist has the id.

#### Scenario: Artist checked
- **WHEN** MarkOfficialSiteChecked is called for an artist with a time
- **THEN** the artist's official_site_check_time is that time

#### Scenario: Artist without an official site
- **WHEN** MarkOfficialSiteChecked is called for an artist that has no official site
- **THEN** the artist's official_site_check_time is set and no official site is created

#### Scenario: Unknown artist
- **WHEN** MarkOfficialSiteChecked is called with an id no artist has
- **THEN** MarkOfficialSiteChecked fails with NotFound
