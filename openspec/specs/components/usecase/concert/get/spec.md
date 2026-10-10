# components/usecase/concert/get Specification

## Purpose
ConcertUseCase.Get returns one Concert by its Event id, for a fan or a link preview opening that Event's page, when its Series has an event page.

## Requirements

### Requirement: Concert with an event page

Get SHALL take an Event id and read the Concert with Concert.ListByIDs, with its Venue, performers and Series, and the Series with Series.Get. When the Series has an event page (see Series), Get SHALL return the Concert with its Series' description, cover image, visibility and publish state. Get needs no signed-in caller.

#### Scenario: Published public concert

- **WHEN** Get is called for an Event of a PUBLISHED PUBLIC first-party Series
- **THEN** it returns the Concert with its Series' description, cover image and publish state PUBLISHED

#### Scenario: Cancelled series

- **WHEN** Get is called for an Event of a CANCELLED PUBLIC first-party Series
- **THEN** it returns the Concert with its Series' publish state CANCELLED

### Requirement: No event page is reported as not found

Get SHALL fail with NotFound, without saying why, when no Concert has the id or when the Concert's Series has no event page. The same failure SHALL be returned for an unknown id, a discovered concert, a DRAFT Series and an UNLISTED Series, so a caller cannot learn whether an unpublished or unlisted event exists.

#### Scenario: Unknown id

- **WHEN** Get is called with an id that matches no Concert
- **THEN** it fails with NotFound

#### Scenario: Unlisted series

- **WHEN** Get is called for an Event of a PUBLISHED UNLISTED Series
- **THEN** it fails with NotFound, exactly as for an unknown id

#### Scenario: Discovered concert

- **WHEN** Get is called for a Concert whose Series has no organizer
- **THEN** it fails with NotFound

### Requirement: Read failures

When Concert.ListByIDs or Series.Get fails for any reason other than not found, Get SHALL fail with that error unchanged and return no Concert.

#### Scenario: Store unavailable

- **WHEN** Series.Get fails with Unavailable
- **THEN** Get fails with Unavailable
