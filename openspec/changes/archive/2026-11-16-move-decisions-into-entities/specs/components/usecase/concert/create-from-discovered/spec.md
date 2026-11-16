## MODIFIED Requirements

### Requirement: One Series per discovered series

For each discovered series, CreateFromDiscovered SHALL look up the Artist's Events on the series' dates (Concert.FindEventsByArtistAndDate). When any of them has the same date and the same listed venue (see Venue, "Same listed venue") as one of the series' events, the series SHALL join that Event's Series — the one with the smallest id when several match. Otherwise a new Series SHALL be created with the discovered title, type and source page (Series.Create) before any of its events is stored or staged. The Series type SHALL come from the discovery, never from the number of events.

#### Scenario: Re-discovered tour joins its series
- **WHEN** a tour is discovered again and one of its dates matches an Event of the Artist at the same venue
- **THEN** all its events go under that Event's Series and no Series is created

#### Scenario: New tour
- **WHEN** none of a tour's events matches an Event of the Artist
- **THEN** one TOUR Series is created and all its events go under it

#### Scenario: Same-day show at another venue does not join
- **WHEN** the Artist has an Event on one of the tour's dates at a different venue
- **THEN** the tour does not join that Event's Series

### Requirement: Re-discovery of the artist's own event

When the Artist already has an Event on an event's date at the same listed venue (see Venue, "Same listed venue"), CreateFromDiscovered SHALL NOT look up the venue. When that Event has the same start time (or both have none), nothing is stored. When the event brings a start time and that Event has none, the time SHALL be filled onto it (Concert.FillEventStartTimes) and nothing else stored; one unknown-start Event SHALL be filled by at most one event of the batch. Otherwise the event SHALL be handled as a resolved event at that Event's Venue.

#### Scenario: Exact re-discovery
- **WHEN** the event matches the Artist's Event at the same venue, date and start time
- **THEN** nothing is stored and no venue is looked up

#### Scenario: Start time announced
- **WHEN** the Artist's Event at that venue and date has no start time and the event starts at 18:00
- **THEN** the Event now starts at 18:00 and no new Event is stored

#### Scenario: Two new start times for one unknown-start event
- **WHEN** the Artist's Event has no start time and the batch brings 13:00 and 18:00 at that venue and date
- **THEN** the Event is filled with 13:00 and 18:00 is handled as a new event
