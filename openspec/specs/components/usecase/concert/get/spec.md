# components/usecase/concert/get Specification

## Purpose
ConcertUseCase.Get returns one Concert by its Event id, for a fan or a link preview opening that Event's page, when its Series has an event page.

## Requirements

### Requirement: Concert with an event page

Get SHALL take an Event id and read the Concert with Concert.ListByIDs, with its Venue, performers, publish state and Series, the Series including its description, cover image, visibility and publish state (`split-concert-from-event` removed the second read with Series.Get). When the Event has an event page (see Series), Get SHALL return the Concert with its own publish state and that Series. Get needs no signed-in caller.

#### Scenario: Published public concert

- **WHEN** Get is called for a PUBLISHED Event of a PUBLIC first-party Series
- **THEN** it returns the Concert with publish state PUBLISHED and its Series' description and cover image

#### Scenario: Cancelled series

- **WHEN** Get is called for a CANCELLED Event of a PUBLIC first-party Series
- **THEN** it returns the Concert with publish state CANCELLED

#### Scenario: Draft date of a published series

- **WHEN** Get is called for a DRAFT Event of a PUBLIC first-party Series whose other Events are PUBLISHED
- **THEN** it fails with NotFound, exactly as for an unknown id

### Requirement: No event page is reported as not found

Get SHALL fail with NotFound, without saying why, when no Concert has the id or when the Concert's Event has no event page (see Series). The same failure SHALL be returned for an unknown id, a discovered concert, a DRAFT Event and an Event of an UNLISTED Series, so a caller cannot learn whether an unpublished or unlisted event exists.

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

When Concert.ListByIDs fails for any reason, Get SHALL fail with that error unchanged and return no Concert.

#### Scenario: Store unavailable

- **WHEN** Concert.ListByIDs fails with Unavailable
- **THEN** Get fails with Unavailable
