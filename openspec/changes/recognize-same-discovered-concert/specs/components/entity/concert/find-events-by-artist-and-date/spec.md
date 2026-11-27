## MODIFIED Requirements

### Requirement: Events of an artist on dates

FindEventsByArtistAndDate SHALL return each Event on one of the given dates whose performers include the Artist, once, with its id, Series, Venue, listed venue name, other listed venue names, local date, start time, publish state and performing Artists. Given no Artist or no dates, or when no Event matches, it SHALL return an empty list without error.

#### Scenario: Artist performs on one of the dates
- **WHEN** the Artist performs on 2026-06-01 and the dates are 2026-06-01 and 2026-06-02
- **THEN** the 2026-06-01 Event is returned

#### Scenario: Other artist's event on the date
- **WHEN** only another Artist performs on 2026-06-01
- **THEN** an empty list is returned

#### Scenario: Other listed venue names returned
- **WHEN** the Artist's Event on 2026-06-01 is listed as "京セラドーム大阪" and also under "Kyocera Dome Osaka"
- **THEN** it is returned with both names

#### Scenario: Shared bill returned with its performers
- **WHEN** the Artist and another Artist perform at an Event of an Organizer's PUBLISHED Series on 2026-06-01
- **THEN** it is returned with both Artists as performers and its publish state PUBLISHED
