# Follow

## Purpose

FollowUseCase.Follow records that a fan follows an artist, announces the follow, and in the background completes what the artist is missing: its official site and, when the artist has never been searched, a first concert search. No failure in the background work changes the result of the follow.

## Requirements

### Requirement: Follow creates the fan's Follow of the artist

Follow SHALL create the fan's Follow of the artist through Follow.Follow and succeed once it is stored. When the Follow cannot be stored, including when the artist does not exist, Follow SHALL fail with Internal and do nothing else.

#### Scenario: Fan follows a new artist

- **WHEN** a fan follows an artist they do not follow
- **THEN** the Follow is stored and Follow succeeds

#### Scenario: Unknown artist

- **WHEN** the artist does not exist
- **THEN** Follow fails with Internal and nothing is announced or started

### Requirement: A repeat follow changes nothing

When the fan already follows the artist, Follow SHALL succeed without changing the Follow or its hype level, without announcing the follow again and without starting any background work.

Known defect: liverty-music/backend#473

#### Scenario: Fan follows the same artist twice

- **WHEN** a fan who follows an artist at Away follows it again
- **THEN** Follow succeeds, the hype level stays Away, and the follow is not announced a second time

### Requirement: Follow announces the new follow

After a new Follow is stored, Follow SHALL announce that the fan followed the artist. A failure to announce SHALL NOT fail the follow.

#### Scenario: Announcement fails

- **WHEN** the follow is stored but announcing it fails
- **THEN** Follow still succeeds

### Requirement: Official site resolved in the background

After a new Follow is stored, Follow SHALL, in the background and after answering the fan, look up the artist's official site when none is stored (Artist.GetOfficialSite returns NotFound) and the artist has an MBID: it reads the artist (Artist.Get), resolves the site from the MBID (Artist.ResolveOfficialSiteURL) and, when a site is found, stores it (Artist.CreateOfficialSite). An artist that already has a site, has no MBID, or has no site in the catalog is left as is. Every failure in this work SHALL be ignored.


#### Scenario: Artist without an official site

- **WHEN** a fan follows an artist that has an MBID, no stored official site, and a site in the catalog
- **THEN** the site is stored for the artist after the follow has been answered

#### Scenario: Artist already has a site

- **WHEN** the followed artist already has an official site
- **THEN** no site is looked up

#### Scenario: Catalog lookup fails

- **WHEN** resolving the site fails
- **THEN** nothing is stored and the follow is unaffected

### Requirement: First concert search requested in the background

After a new Follow is stored, Follow SHALL, in the background and after answering the fan, read the artist's search history (SearchLog.GetByArtistID). When the artist has never been searched (NotFound), Follow SHALL request a concert search for the artist; the search itself belongs to concert search. When the history exists, or cannot be read for any other reason, no search is requested. A failed search SHALL NOT affect the follow.

#### Scenario: Artist never searched

- **WHEN** a fan follows an artist with no search history
- **THEN** a concert search for the artist is requested after the follow has been answered

#### Scenario: Artist searched before

- **WHEN** a fan follows an artist that has a search history
- **THEN** no concert search is requested

#### Scenario: Search history unreadable

- **WHEN** reading the search history fails with an error other than NotFound
- **THEN** no concert search is requested and the follow is unaffected

#### Scenario: Search fails

- **WHEN** the requested concert search fails
- **THEN** the follow has already succeeded and is unaffected
