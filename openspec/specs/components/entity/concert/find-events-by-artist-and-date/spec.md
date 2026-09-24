# Concert.FindEventsByArtistAndDate

## Purpose

Finds the Events at which an Artist already performs on any of the given local dates, with the fields needed to decide identity and parentage.

## Requirements

### Requirement: Events of an artist on dates

FindEventsByArtistAndDate SHALL return each Event on one of the given dates whose performers include the Artist, once, with its id, Series, Venue, listed venue name, local date and start time. Given no Artist or no dates, or when no Event matches, it SHALL return an empty list without error.

#### Scenario: Artist performs on one of the dates
- **WHEN** the Artist performs on 2026-06-01 and the dates are 2026-06-01 and 2026-06-02
- **THEN** the 2026-06-01 Event is returned

#### Scenario: Other artist's event on the date
- **WHEN** only another Artist performs on 2026-06-01
- **THEN** an empty list is returned
