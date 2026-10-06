# Spec Delta

## ADDED Requirements

### Requirement: Only series that need a search are searched

DiscoverForArtist SHALL search a series of the artist only when all of these hold:

- TicketJourney.ListUserIDsTrackingSeries returns at least one fan for it.
- It has an upcoming event (Concert.ListByArtist with upcoming concerts only).
- No phase returned by SalesPhase.GetBySeries for it has an application that has not ended.
- SalesPhaseSearchLog.ListBySeries shows it was never searched, or last searched 30 days or more ago.

DiscoverForArtist SHALL call SalesPhase.SearchSalesPhases once for the artist with the artist's official site and every series that qualifies, each with its title and the event period of its upcoming events. It SHALL return 0 without searching in either of these cases:

- No series qualifies.
- The artist has no official site, or an empty one.

When the artist's concerts, its official site, a series' trackers, phases or search log cannot be read, DiscoverForArtist SHALL fail with that error.

#### Scenario: Tracked series with nothing pending

- **WHEN** a fan tracks a series with an upcoming event, the series has no phase, and it was last searched 40 days ago
- **THEN** SearchSalesPhases is called with that series

#### Scenario: Nobody tracks the series

- **WHEN** an artist's only upcoming series is tracked by no fan
- **THEN** no search runs and DiscoverForArtist returns 0

#### Scenario: A phase is still open

- **WHEN** a tracked series has a stored lottery that closes next week
- **THEN** the series is not searched

#### Scenario: First-come sale until sold out has opened

- **WHEN** a tracked series' only stored phase is a first-come sale with no apply end time that opened yesterday, and the series was last searched 31 days ago
- **THEN** the series is searched

#### Scenario: Searched recently

- **WHEN** a tracked series with nothing pending was last searched 10 days ago
- **THEN** the series is not searched

#### Scenario: Events far ahead

- **WHEN** a tracked series' only events are 10 months away and nothing is pending
- **THEN** the series is searched

#### Scenario: Two tracked series

- **WHEN** two series of the artist qualify
- **THEN** SearchSalesPhases is called once with both series

#### Scenario: No official site

- **WHEN** a series qualifies and the artist has no official site
- **THEN** no search runs and DiscoverForArtist returns 0 without an error

### Requirement: A successful search is recorded

When SearchSalesPhases succeeds, DiscoverForArtist SHALL call SalesPhaseSearchLog.Record for every series it searched, with the time of the search, whether or not any phase was found. When the search fails, nothing SHALL be recorded, so the next daily run searches those series again. When recording fails, DiscoverForArtist SHALL fail with that error after storing the discovered phases.

#### Scenario: Search finds nothing

- **WHEN** SearchSalesPhases returns no phases for a searched series
- **THEN** the series' search is recorded and it is not searched again for 30 days

#### Scenario: Search fails

- **WHEN** SearchSalesPhases fails with ResourceExhausted
- **THEN** no search is recorded and the series is searched again on the next daily run

## REMOVED Requirements

### Requirement: One search per artist over its series in the next 90 days

**Reason**: Searching every series with an event in the next 90 days every day cost search queries for series nobody tracks. It also missed the presales of tours more than 90 days away.
**Migration**: Replaced by "Only series that need a search are searched" and "A successful search is recorded". The 90-day window setting is removed.
