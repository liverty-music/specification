# Discover For Artist

## Purpose

DiscoverForArtist finds the currently open or upcoming ticket sales phases for one artist's upcoming series and stores them, updating phases already known and creating new ones. Each newly created phase is handed on to be announced to the fans tracking its series, and the method returns the number of new phases.

## Requirements

### Requirement: Daily discovery over every followed artist

DiscoverForArtist SHALL run once a day at 21:00 Japan time for each artist that at least one fan follows, one artist at a time.

#### Scenario: Daily run

- **WHEN** the daily discovery time is reached
- **THEN** DiscoverForArtist runs once for each followed artist

### Requirement: One search per artist over its series in the next 90 days

DiscoverForArtist SHALL collect the artist's series that have an upcoming event within the next 90 days, each with its title and those events' dates, and SHALL call SalesPhase.SearchSalesPhases once for the artist with the artist's official site and those series. It SHALL return 0 without searching when the artist has no such series, or when the artist has no official site or an empty one. When the artist's concerts or official site cannot be read for another reason, DiscoverForArtist SHALL fail with that error.

#### Scenario: Two series in the window

- **WHEN** an artist has upcoming events of two series within the next 90 days
- **THEN** SearchSalesPhases is called once with both series

#### Scenario: Events only beyond 90 days

- **WHEN** an artist's only upcoming events are 120 days away
- **THEN** no search runs and DiscoverForArtist returns 0

#### Scenario: No official site

- **WHEN** the artist has no official site
- **THEN** no search runs and DiscoverForArtist returns 0 without an error

### Requirement: Each discovered phase is stored

DiscoverForArtist SHALL pass each discovered phase to SalesPhase.Upsert. A phase that cannot be stored SHALL be skipped and the remaining phases SHALL still be stored. When the search fails, DiscoverForArtist SHALL fail with the search's error and store nothing.

#### Scenario: One phase cannot be stored

- **WHEN** the search returns three phases and storing the second fails
- **THEN** the first and third phases are stored and DiscoverForArtist succeeds

#### Scenario: Search fails

- **WHEN** SearchSalesPhases fails
- **THEN** DiscoverForArtist fails with that error

### Requirement: Only a newly created phase is announced

For each phase that Upsert reports as Inserted, DiscoverForArtist SHALL request its announcement to the fans tracking the series (see AnnounceDiscoveredPhase) and count it as new. A phase reported as Updated or Skipped SHALL NOT be announced. A request that cannot be queued SHALL NOT undo the stored phase and SHALL NOT be retried, so that phase is never announced. DiscoverForArtist SHALL return the number of phases reported as Inserted.

#### Scenario: New phase

- **WHEN** a discovered phase is created
- **THEN** its announcement is requested and it counts towards the returned number

#### Scenario: Known phase discovered again

- **WHEN** a discovered phase updates a phase already known
- **THEN** no announcement is requested and it is not counted

#### Scenario: Announcement request fails

- **WHEN** a phase is created and its announcement request cannot be queued
- **THEN** the phase stays stored, it is counted as new, and it is not announced later
