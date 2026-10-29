# Spec Delta

## ADDED Requirements

### Requirement: A series is searched only when it needs a search

DiscoverForArtist SHALL search a series of the artist only when all of these hold:

- It has no Organizer. A first-party Series sells only through its Organizer's own TicketSales.
- TicketJourney.ListUserIDsTrackingSeries returns at least one fan for it.
- It has an upcoming event (Concert.ListByArtist with upcoming concerts only).
- No sale returned by TicketSale.ListBySeries for it is not yet over.
- TicketSaleSearch.ListBySeries shows it was never searched, or last searched 10 or more days ago. Days are counted as calendar days in Japan time (Asia/Tokyo), so a series searched on a given date is searched again from the run 10 dates later, whatever the time of day of either run.

DiscoverForArtist SHALL call TicketSale.SearchPublishedSales once for the artist with the artist's official site and every series that qualifies, each with its title and the event period of its upcoming events. It SHALL return 0 without searching in either of these cases:

- No series qualifies.
- The artist has no official site, or an empty one.

When the artist's concerts, its official site, a series' trackers, sales or ticket sale search cannot be read, DiscoverForArtist SHALL fail with that error.

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

## REMOVED Requirements

### Requirement: Only series that need a search are searched

**Reason**: Every sale now has an end time, so the case of a first-come sale without an end time is gone.
**Migration**: See "A series is searched only when it needs a search"; the conditions are unchanged.
