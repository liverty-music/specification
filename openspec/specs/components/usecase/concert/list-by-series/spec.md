# components/usecase/concert/list-by-series Specification

## Purpose
ConcertUseCase.ListBySeries returns every Concert of one Series that has an event page, so an Event page can offer the Series' other dates and a link preview can count them.

## Requirements

### Requirement: Concerts of a series with an event page

ListBySeries SHALL take a Series id, read the Series with Series.Get, and when the Series has an event page (see Series), return its Concerts: the Events listed by Concert.ListEventsBySeries, in that operation's order, each read with Concert.ListByIDs with its Venue, performers and Series. ListBySeries needs no signed-in caller.

#### Scenario: Two-day run

- **WHEN** ListBySeries is called for a PUBLISHED PUBLIC first-party Series with Events on 2026-11-21 and 2026-11-20
- **THEN** it returns two Concerts, the 2026-11-20 one first

#### Scenario: Same day, two shows

- **WHEN** the Series has Events on 2026-11-20 at 13:00 and at 18:00
- **THEN** the 13:00 Concert is returned before the 18:00 Concert

### Requirement: No event page is reported as not found

ListBySeries SHALL fail with NotFound, without saying why, when no Series has the id or when the Series has no event page, the same for an unknown id, a discovered Series, a DRAFT Series and an UNLISTED Series.

#### Scenario: Unlisted series

- **WHEN** ListBySeries is called for a PUBLISHED UNLISTED Series
- **THEN** it fails with NotFound, exactly as for an unknown id

#### Scenario: Discovered series

- **WHEN** ListBySeries is called for a Series with no organizer
- **THEN** it fails with NotFound

### Requirement: Read failures

When Series.Get, Concert.ListEventsBySeries or Concert.ListByIDs fails for any reason other than not found, ListBySeries SHALL fail with that error unchanged and return no Concert.

#### Scenario: Store unavailable

- **WHEN** Concert.ListEventsBySeries fails with Unavailable
- **THEN** ListBySeries fails with Unavailable
