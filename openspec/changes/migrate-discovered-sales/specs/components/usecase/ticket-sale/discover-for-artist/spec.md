# Spec Delta

## Purpose

TicketSaleDiscoveryUseCase.DiscoverForArtist finds the ticket sales that have not opened yet for the series of one artist that fans track and that need a search, and stores them as discovered TicketSales. It updates sales already known, creates new ones and records each searched series. Each newly created sale is handed on to be announced to the fans tracking its series, and the method returns the number of new sales.

## ADDED Requirements

### Requirement: Daily discovery over every followed artist

DiscoverForArtist SHALL run once a day at 21:00 Japan time for each artist that at least one fan follows (Follow.ListAll), one artist at a time.

#### Scenario: Daily run
- **WHEN** the daily discovery time is reached
- **THEN** DiscoverForArtist runs once for each followed artist

### Requirement: Each discovered sale is stored

DiscoverForArtist SHALL pass each discovered sale to TicketSale.UpsertDiscovered. A sale that cannot be stored SHALL be skipped and the remaining sales SHALL still be stored. When the search fails, DiscoverForArtist SHALL fail with the search's error and store nothing.

#### Scenario: One sale cannot be stored
- **WHEN** the search returns three sales and storing the second fails
- **THEN** the first and third sales are stored and DiscoverForArtist succeeds

#### Scenario: Search fails
- **WHEN** TicketSale.SearchPublishedSales fails
- **THEN** DiscoverForArtist fails with that error

### Requirement: Only a newly created sale is announced

For each sale that UpsertDiscovered reports as Inserted, DiscoverForArtist SHALL request its announcement to the fans tracking the series (see TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale) and count it as new. A sale reported as Updated or Skipped SHALL NOT be announced. A request that cannot be queued SHALL NOT undo the stored sale and SHALL NOT be retried, so that sale is never announced. DiscoverForArtist SHALL return the number of sales reported as Inserted.

#### Scenario: New sale
- **WHEN** a discovered sale is created
- **THEN** its announcement is requested and it counts towards the returned number

#### Scenario: Known sale discovered again
- **WHEN** a discovered sale updates a sale already known
- **THEN** no announcement is requested and it is not counted

#### Scenario: Announcement request fails
- **WHEN** a sale is created and its announcement request cannot be queued
- **THEN** the sale stays stored, it is counted as new, and it is not announced later

### Requirement: Only series that need a search are searched

DiscoverForArtist SHALL search a series of the artist only when all of these hold:

- It has no Organizer. A first-party Series sells only through its Organizer's own TicketSales.
- TicketJourney.ListUserIDsTrackingSeries returns at least one fan for it.
- It has an upcoming event (Concert.ListByArtist with upcoming concerts only).
- No sale returned by TicketSale.ListBySeries for it is not yet over.
- TicketSaleSearchLog.ListBySeries shows it was never searched, or last searched 10 or more days ago. Days are counted as calendar days in Japan time (Asia/Tokyo), so a series searched on a given date is searched again from the run 10 dates later, whatever the time of day of either run.

DiscoverForArtist SHALL call TicketSale.SearchPublishedSales once for the artist with the artist's official site and every series that qualifies, each with its title and the event period of its upcoming events. It SHALL return 0 without searching in either of these cases:

- No series qualifies.
- The artist has no official site, or an empty one.

When the artist's concerts, its official site, a series' trackers, sales or search log cannot be read, DiscoverForArtist SHALL fail with that error.

#### Scenario: Tracked series with nothing pending
- **WHEN** a fan tracks a series with an upcoming event, the series has no sale, and it was last searched 12 days ago
- **THEN** SearchPublishedSales is called with that series

#### Scenario: Organizer's series
- **WHEN** a fan tracks an upcoming event of the artist's Series that an Organizer owns, and nothing is pending
- **THEN** that Series is not searched

#### Scenario: Nobody tracks the series
- **WHEN** an artist's only upcoming series is tracked by no fan
- **THEN** no search runs and DiscoverForArtist returns 0

#### Scenario: A sale is still open
- **WHEN** a tracked series has a stored lottery that closes next week
- **THEN** the series is not searched

#### Scenario: First-come sale until sold out has opened
- **WHEN** a tracked series' only stored sale is a first-come sale with no end time that opened yesterday, and the series was last searched 11 days ago
- **THEN** the series is searched

#### Scenario: Searched recently
- **WHEN** a tracked series with nothing pending was last searched 5 days ago
- **THEN** the series is not searched

#### Scenario: Ten days counted by date
- **WHEN** a tracked series with nothing pending was last searched on 7 October at 21:00:30 Japan time and the run on 17 October starts at 21:00:00
- **THEN** the series is searched

#### Scenario: Nine days counted by date
- **WHEN** a tracked series with nothing pending was last searched on 7 October at 21:00:30 Japan time and the run on 16 October starts at 23:59
- **THEN** the series is not searched

#### Scenario: Events far ahead
- **WHEN** a tracked series' only events are 10 months away and nothing is pending
- **THEN** the series is searched

#### Scenario: Two tracked series
- **WHEN** two series of the artist qualify
- **THEN** SearchPublishedSales is called once with both series

#### Scenario: No official site
- **WHEN** a series qualifies and the artist has no official site
- **THEN** no search runs and DiscoverForArtist returns 0 without an error

### Requirement: A successful search is recorded

When SearchPublishedSales succeeds, DiscoverForArtist SHALL call TicketSaleSearchLog.Record for every series it searched, with the time of the search, whether or not any sale was found. When the search fails, nothing SHALL be recorded, so the next daily run searches those series again. When recording fails, DiscoverForArtist SHALL fail with that error after storing the discovered sales.

#### Scenario: Search finds nothing
- **WHEN** SearchPublishedSales returns no sales for a searched series
- **THEN** the series' search is recorded and it is not searched again for 10 days

#### Scenario: Search fails with a spend cap
- **WHEN** SearchPublishedSales fails with ResourceExhausted
- **THEN** no search is recorded and the series is searched again on the next daily run
