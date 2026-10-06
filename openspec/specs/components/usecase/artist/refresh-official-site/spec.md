# OfficialSiteRefreshUseCase.RefreshOfficialSite

## Purpose

OfficialSiteRefreshUseCase.RefreshOfficialSite keeps an artist's official site in line with the music catalog, so discovery reads the artist's current site. It runs daily for a small batch of followed artists whose site was never checked or was checked more than 7 days ago.

## Requirements

### Requirement: RefreshOfficialSite brings the stored site in line with the catalog
OfficialSiteRefreshUseCase.RefreshOfficialSite SHALL take an artist id and MBID, look the homepage up with Artist.ResolveOfficialSiteURL and then:
- when a URL is found and the artist has no official site (Artist.GetOfficialSite returns NotFound), store it as a new OfficialSite with Artist.CreateOfficialSite;
- when a URL is found and it differs from the stored site's url, replace it with Artist.UpdateOfficialSiteURL;
- when the found URL equals the stored url, or no URL is found, leave the stored site as it is.
After that it SHALL record the check with Artist.MarkOfficialSiteChecked at the current time.

#### Scenario: Catalog resolves to a different site
- **WHEN** the stored site is `http://hitsujibungaku.jimdo.com/` and the catalog resolves to `https://www.hitsujibungaku.info/`
- **THEN** the stored site keeps its id, its url becomes `https://www.hitsujibungaku.info/`, and the check time is now

#### Scenario: Catalog resolves to the stored site
- **WHEN** the catalog resolves to the URL already stored
- **THEN** the stored site is unchanged and the check time is now

#### Scenario: Artist without a site gets one
- **WHEN** the artist has no official site and the catalog resolves to a URL
- **THEN** that URL is stored as the artist's official site with a fresh id, and the check time is now

#### Scenario: Catalog lists no active homepage
- **WHEN** the artist has a stored site and the catalog resolves to no URL
- **THEN** the stored site is kept and the check time is now

#### Scenario: No site anywhere
- **WHEN** the artist has no official site and the catalog resolves to no URL
- **THEN** no site is stored and the check time is now

### Requirement: RefreshOfficialSite reports failures without recording a check
When Artist.ResolveOfficialSiteURL, Artist.GetOfficialSite (other than NotFound), Artist.CreateOfficialSite or Artist.UpdateOfficialSiteURL fails, OfficialSiteRefreshUseCase.RefreshOfficialSite SHALL fail with that error and SHALL NOT record a check, so the artist stays due. It SHALL fail with the error of Artist.MarkOfficialSiteChecked.

#### Scenario: Catalog unreachable
- **WHEN** Artist.ResolveOfficialSiteURL fails with Unavailable
- **THEN** RefreshOfficialSite fails with Unavailable, the stored site is unchanged and no check time is recorded

### Requirement: RefreshOfficialSite runs daily for a small batch of due artists
Once a day at 04:00 Japan time, RefreshOfficialSite SHALL run, one artist at a time in the returned order, for the artists returned by Artist.ListStaleOfficialSite with an age of 7 days and a limit of the number of artists returned by Follow.ListAll divided by 7, rounded up. When nobody follows any artist, the run SHALL do nothing. The run SHALL stop after 3 consecutive failed artists and SHALL stop when it is asked to shut down; a failed artist does not stop the run otherwise.

#### Scenario: Batch size
- **WHEN** 133 artists are followed and 40 of them are due
- **THEN** the run refreshes the 19 artists returned first

#### Scenario: Nobody followed
- **WHEN** no fan follows any artist
- **THEN** the run refreshes nobody

#### Scenario: Consecutive failures
- **WHEN** the catalog is unreachable for 3 artists in a row
- **THEN** the run stops and the remaining artists stay due for the next run
