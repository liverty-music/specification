## MODIFIED Requirements

### Requirement: One Series per discovered series

For each discovered series, CreateFromDiscovered SHALL look up the Artist's Events on the series' dates (Concert.FindEventsByArtistAndDate) and decide the Venue of each of its events (see "Re-discovery of the artist's own event" and "Venue resolution") before choosing the series' Series, in this order:

1. the Series of one of those Events that the Artist performs at alone and that has no publish state, that has the date of one of the series' events, and that either is listed under that event's listed venue name (see Event, "Listed under a name") or is at that event's Venue — the one with the smallest id when several match;
2. for a TOUR series only, the Series with the same tour title (see Series, "Same tour title") among the Artist's upcoming discovered tours at the current time (Series.ListUpcomingToursByArtist) — the one with the smallest id when several match;
3. otherwise a new Series created with the discovered title, type and source page (Series.Create) before any of its events is stored or staged.

A SINGLE series SHALL never join a Series by its title. The Series type SHALL come from the discovery, never from the number of events.

#### Scenario: Re-discovered tour joins its series
- **WHEN** a tour is discovered again and one of its dates matches an Event of the Artist at the same venue
- **THEN** all its events go under that Event's Series and no Series is created

#### Scenario: New tour
- **WHEN** none of a tour's events matches an Event of the Artist and the Artist has no upcoming discovered tour of the same title
- **THEN** one TOUR Series is created and all its events go under it

#### Scenario: Same-day show at another venue does not join
- **WHEN** the Artist has an Event on one of the tour's dates at a different venue
- **THEN** the tour does not join that Event's Series

#### Scenario: Same venue under another name joins
- **WHEN** a tour lists "京セラドーム大阪" on 2026-12-19, it resolves to Venue V, and the Artist's Event at V on 2026-12-19 is listed as "Kyocera Dome Osaka"
- **THEN** the tour's events go under that Event's Series

#### Scenario: Dates announced later join their tour
- **WHEN** a tour titled "2026 LE SSERAFIM TOUR “PUREFLOW”" brings only dates the Artist has no Event on, and the Artist's discovered TOUR Series "2026 LE SSERAFIM TOUR 'PUREFLOW'" has an Event after the current date
- **THEN** the tour's events go under that Series and no Series is created

#### Scenario: Tour already over is not joined
- **WHEN** the Artist's discovered TOUR Series of the same title has only Events dated before the current date
- **THEN** a new TOUR Series is created

#### Scenario: Shared bill does not pull the tour into another Artist's Series
- **WHEN** the Artist performs together with another Artist at an Event of the other Artist's Series on one of the tour's dates, and at no other Event on its dates
- **THEN** the tour does not join that Series

#### Scenario: Standalone show is not joined by title
- **WHEN** a SINGLE series titled "Live" is discovered and the Artist has an upcoming SINGLE Series titled "Live"
- **THEN** a new SINGLE Series is created

### Requirement: Re-discovery of the artist's own event

When the Artist has an Event on an event's date listed under the event's listed venue name (see Event, "Listed under a name"), CreateFromDiscovered SHALL NOT look up the venue and SHALL use that Event's Venue; otherwise the event's Venue comes from "Venue resolution". Once the Venue is known, CreateFromDiscovered SHALL compare the event with the Artist's Events at that Venue and date, whatever names they are listed under:

- when one of them has the same start time (or both have none) and is listed under the event's name, nothing SHALL be stored;
- when the event has no start time and one of them, listed under the event's name, has one, nothing SHALL be stored, since the event adds nothing;
- when the event has no start time and one of them, not listed under the event's name, has one, the event SHALL be staged (ConcertCandidate.Upsert) and not published;
- when one of them has the same start time (or both have none) and is not listed under the event's name, the event SHALL be staged (ConcertCandidate.Upsert) and not published;
- when the event brings a start time and one of them has none, the time SHALL be filled onto that Event (Concert.FillEventStartTimes) and nothing else stored, unless that Event has a publish state (an Organizer's Event is never filled: nothing is stored when it is listed under the event's name, and the event is staged otherwise), unless the Artist has an Event with that start time at another Venue (see "Same Artist at another venue at the same time") or another Event holds that slot (see "Start time held by another Event"); one unknown-start Event SHALL be filled by at most one event of the batch;
- otherwise the event SHALL go on to "Same Artist at another venue at the same time" and then to the collision check.

#### Scenario: Exact re-discovery
- **WHEN** the event matches the Artist's Event at the same venue, date and start time
- **THEN** nothing is stored and no venue is looked up

#### Scenario: Start time announced
- **WHEN** the Artist's Event at that venue and date has no start time and the event starts at 18:00
- **THEN** the Event now starts at 18:00 and no new Event is stored

#### Scenario: Two new start times for one unknown-start event
- **WHEN** the Artist's Event has no start time and the batch brings 13:00 and 18:00 at that venue and date
- **THEN** the Event is filled with 13:00 and 18:00 is handled as a new event

#### Scenario: Start time announced under another name
- **WHEN** the Artist's Event at Venue V on 2026-12-19 is listed as "Kyocera Dome Osaka" without a start time, and the event lists "京セラドーム大阪" at 17:00 and resolves to V
- **THEN** that Event now starts at 17:00 and no new Event is stored

#### Scenario: Same show under another name
- **WHEN** the Artist's Event at Venue V on 2026-12-19 is listed as "京セラドーム大阪" at 17:00, and the event lists "Kyocera Dome Osaka" at 17:00 and resolves to V
- **THEN** the event is staged and nothing is published

#### Scenario: Start time unknown in a later listing
- **WHEN** the Artist's Event at Venue V is listed as "Zepp Haneda(TOKYO)" at 18:00 and the event lists "Zepp Haneda(TOKYO)" without a start time
- **THEN** nothing is stored

#### Scenario: Start time unknown under another name
- **WHEN** the Artist's Event at Venue V is listed as "京セラドーム大阪" at 17:00 and the event lists "Kyocera Dome Osaka" without a start time and resolves to V
- **THEN** the event is staged and nothing is published

#### Scenario: Name kept from an earlier review
- **WHEN** the Artist's Event is listed as "京セラドーム大阪" at 17:00 with "Kyocera Dome Osaka" among its other listed venue names, and the event lists "Kyocera Dome Osaka" at 17:00
- **THEN** nothing is stored and no venue is looked up

### Requirement: Collision is staged, anything else is published

For a resolved event that the requirements above did not settle, CreateFromDiscovered SHALL look up the Events at its Venue and date (Concert.FindEventsByVenueAndDate), all of them other Artists' Events at this point:

- when one of them has no publish state, has the same known start time and is listed under the event's listed venue name, the event SHALL be published: Concert.Create stores it in that Event's slot, which adds the Artist to its performers;
- otherwise the event collides when an Event there has the same start time (or both have none), or when the event has no start time and an Event there has one, and a colliding event SHALL be staged (ConcertCandidate.Upsert) and not published; it carries the resolved place id when its venue was looked up, and none when it reused the Artist's existing Event's Venue;
- any other event SHALL be published under the series' Series with the Artist as performer.

Published events go out together with the series' other published events (see "The published events of a series are created together"). The RejectedConcert SHALL NOT be consulted.

#### Scenario: Same slot as an existing event
- **WHEN** another Artist's Event at the resolved Venue, date and start time exists under another listed venue name
- **THEN** the event is staged with its resolved place id and not published

#### Scenario: Shared bill under the same name
- **WHEN** Artist B's Event at Venue V on 2026-12-22 starts at 18:00 and is listed as "Zepp Haneda(TOKYO)", and Artist A's event lists "Zepp Haneda (TOKYO)" at 18:00 and resolves to V
- **THEN** no Event is added, A and B both perform at that Event, and A's followers are told about it

#### Scenario: Organizer's event at the same slot
- **WHEN** an Organizer's Event at the resolved Venue, date and start time is listed under the event's name
- **THEN** the event is staged and the Organizer's Event is unchanged

#### Scenario: Shared bill without a start time
- **WHEN** another Artist's Event at the resolved Venue and date has no start time and the event has none
- **THEN** the event is staged

#### Scenario: Unknown start next to a known start
- **WHEN** the event has no start time and an Event at that Venue and date starts at 18:00
- **THEN** the event is staged

#### Scenario: Known start next to an unknown-start event
- **WHEN** the event starts at 18:00 and the only Event at that Venue and date is another Artist's, without a start time
- **THEN** a new Event starting at 18:00 is published

#### Scenario: Genuinely new
- **WHEN** no Event is at the resolved Venue and date
- **THEN** the event is published under the series' Series

### Requirement: Empty new series are removed

At the end of the batch, CreateFromDiscovered SHALL remove, among the Series it created in this batch and the Series of the Events it merged away in this batch, those that have no Event and no ConcertCandidate (Series.DeleteOrphaned); it SHALL NOT touch other Series. A failure here SHALL NOT fail the batch.

#### Scenario: Created series left empty
- **WHEN** a Series created in this batch ended up with no Event and no ConcertCandidate
- **THEN** it is removed

#### Scenario: Series of a merged event left empty
- **WHEN** the batch merged away the only Event of a Series that has no ConcertCandidate
- **THEN** that Series is removed at the end of the batch, after every event of the batch was stored

### Requirement: The published events of a series are created together

For each series, CreateFromDiscovered SHALL publish every event it decides to publish in one Concert.Create call with the Artist as performer, after deciding for each event of the series whether to publish, stage, fill, merge or skip it. Each Concert in the call is under the series' Series, except one stored in another Artist's Event slot (see "Collision is staged, anything else is published"), which is under that Event's Series. Concert.Create then tells the Artist's followers about them once per Series. A series that publishes nothing SHALL NOT call Concert.Create. When Concert.Create fails, the batch SHALL fail.

#### Scenario: Three-stop tour
- **WHEN** three events of a tour are to be published
- **THEN** Concert.Create is called once with the three events

#### Scenario: Everything staged
- **WHEN** every event of a series is staged
- **THEN** Concert.Create is not called for that series

#### Scenario: Concerts cannot be created
- **WHEN** Concert.Create fails with Unavailable for a series
- **THEN** CreateFromDiscovered fails and the batch is processed again later

#### Scenario: New date and a shared bill in one series
- **WHEN** a tour brings one new date and one date at another Artist's Event slot under the same listed venue name and start time
- **THEN** Concert.Create is called once with both Concerts, the second under the other Artist's Event's Series

## ADDED Requirements

### Requirement: Same Artist at another venue at the same time

When the event brings a start time and the Artist has an Event on its date with the same start time at another Venue, an Event already stored, one this series publishes, or one it has filled or merged into earlier in the batch, CreateFromDiscovered SHALL stage the event (ConcertCandidate.Upsert) and not publish it, since one Artist cannot play two venues at once.

#### Scenario: Renamed hall
- **WHEN** the Artist's Event on 2027-08-28 at 18:00 is at the Venue listed "日本ガイシホール", and the event lists "クロコくんホール (旧 日本ガイシホール)" at 18:00 and resolves to another Venue
- **THEN** the event is staged and nothing is published

#### Scenario: Two shows of one day at two venues
- **WHEN** the Artist's Event on 2026-12-06 starts at 13:00 at one Venue and the event starts at 19:00 at another
- **THEN** the event is not staged for this reason

### Requirement: Start time held by another Event

When the start time to fill onto the Artist's Event is already held by another Event at that Venue and date (an Event of another Artist), CreateFromDiscovered SHALL treat the two as one concert:

- when that other Event is listed under the event's listed venue name and neither Event has a publish state, it SHALL merge the Artist's Event into it (Concert.Merge), which tells nobody again, and store nothing else;
- otherwise it SHALL stage the event (ConcertCandidate.Upsert) and not publish it.

When filling fails with AlreadyExists because another Event took the slot meanwhile, the event SHALL be staged. Neither case SHALL fail the batch; the batch goes on with its other events.

#### Scenario: Co-headliner's time already known
- **WHEN** Artist A's Event at Venue V on 2026-12-31 has no start time, Artist B's Event at V on 2026-12-31 starts at 18:00 under the same listed venue name, and A's event brings 18:00
- **THEN** A performs at B's 18:00 Event, A's Event without a start time is gone, A's followers are not told again, and the batch's other events are processed

#### Scenario: Held under another name
- **WHEN** the same holds but B's Event is listed under another venue name
- **THEN** A's event is staged and A's Event without a start time is unchanged

#### Scenario: Held by an Organizer's event
- **WHEN** the slot is held by an Organizer's Event listed under the event's name
- **THEN** the event is staged and both Events are unchanged

#### Scenario: Slot taken meanwhile
- **WHEN** filling fails with AlreadyExists
- **THEN** the event is staged and the batch does not fail
