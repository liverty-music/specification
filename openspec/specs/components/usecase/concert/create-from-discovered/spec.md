# Create From Discovered

## Purpose

CreateFromDiscovered takes one Artist's batch of newly discovered series, triggered when a discovery is announced. For each event it does one of four things: publishes it under its Series and announces it to followers; stages it for admin review when its venue is unresolved or its slot collides with an Event already in the catalog; skips it when its slot is suppressed; or fills an announced start time onto the Artist's existing Event.

## Requirements

### Requirement: Triggered by a discovery announcement

CreateFromDiscovered SHALL run once for each discovery announced for an Artist, with that Artist and its DiscoveredSeries. When it fails, the same discovery SHALL be processed again; every step SHALL be safe to repeat.

#### Scenario: Redelivered discovery
- **WHEN** a discovery that was already fully processed is processed again
- **THEN** no Event, Series or StagedConcert is added a second time

### Requirement: Unusable input is skipped

CreateFromDiscovered SHALL skip a series with no title or no events, and an event whose listed venue name is blank after normalization, and continue with the rest. It SHALL normalize every listed venue name before using or storing it.

#### Scenario: Untitled series
- **WHEN** a discovered series has an empty title
- **THEN** none of its events is published or staged and the other series are processed

#### Scenario: Venue to be announced
- **WHEN** an event's listed venue name is blank
- **THEN** that event is skipped

#### Scenario: Prefixed venue name stored normalized
- **WHEN** an event lists "大阪・フェスティバルホール"
- **THEN** whatever is stored for it lists "フェスティバルホール"

### Requirement: One Series per discovered series

For each discovered series, CreateFromDiscovered SHALL look up the Artist's Events on the series' dates (Concert.FindEventsByArtistAndDate). When any of them has the same date and normalized listed venue name as one of the series' events, the series SHALL join that Event's Series — the one with the smallest id when several match. Otherwise a new Series SHALL be created with the discovered title, type and source page (Series.Create) before any of its events is stored or staged. The Series type SHALL come from the discovery, never from the number of events.

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

When the Artist already has an Event on an event's date at the same normalized listed venue, CreateFromDiscovered SHALL NOT look up the venue. When that Event has the same start time (or both have none), nothing is stored. When the event brings a start time and that Event has none, the time SHALL be filled onto it (Concert.FillEventStartTimes) and nothing else stored; one unknown-start Event SHALL be filled by at most one event of the batch. Otherwise the event SHALL be handled as a resolved event at that Event's Venue.

#### Scenario: Exact re-discovery
- **WHEN** the event matches the Artist's Event at the same venue, date and start time
- **THEN** nothing is stored and no venue is looked up

#### Scenario: Start time announced
- **WHEN** the Artist's Event at that venue and date has no start time and the event starts at 18:00
- **THEN** the Event now starts at 18:00 and no new Event is stored

#### Scenario: Two new start times for one unknown-start event
- **WHEN** the Artist's Event has no start time and the batch brings 13:00 and 18:00 at that venue and date
- **THEN** the Event is filled with 13:00 and 18:00 is handled as a new event

### Requirement: Venue resolution

For any other event, CreateFromDiscovered SHALL look up the venue by its listed name and admin area (Venue.SearchPlace), at most once per name and admin area within the batch. When the place is found, the Venue SHALL be found or created in this order: by place id (Venue.GetByPlaceID); by listed venue name and admin area (Venue.GetByListedName), giving that Venue the place id when it has none (Venue.BackfillPlaceID); otherwise created with the place's canonical name, place id, coordinates, the listed venue name and the discovered admin area (Venue.Create). Any lookup failure other than no match SHALL fail the whole batch.

#### Scenario: Known place
- **WHEN** the place is found and a Venue holds its place id
- **THEN** that Venue is used and no Venue is created

#### Scenario: Place id differs from the stored venue
- **WHEN** the place's id matches no Venue but a Venue holds the listed venue name and admin area without a place id
- **THEN** that Venue is used and takes the place id

#### Scenario: Catalog unavailable
- **WHEN** the venue lookup fails with Unavailable
- **THEN** CreateFromDiscovered fails and the discovery is processed again later

### Requirement: Unresolved venue is staged

When the venue lookup finds no match, CreateFromDiscovered SHALL stage the event (StagedConcert.Upsert) with no resolved preview, SHALL NOT create a Venue and SHALL NOT publish it.

#### Scenario: Venue not found
- **WHEN** the venue lookup finds no match
- **THEN** a StagedConcert without resolved place is stored and nothing is published

### Requirement: Suppressed slot is skipped

For a resolved event, CreateFromDiscovered SHALL check its Venue, date and start time (SuppressedConcert.Exists) and, when suppressed, SHALL neither publish nor stage it.

#### Scenario: Deleted concert rediscovered
- **WHEN** the event's slot was suppressed by an admin's delete
- **THEN** it is neither published nor staged

### Requirement: Collision is staged, anything else is published

For a resolved, unsuppressed event, CreateFromDiscovered SHALL look up the Events at its Venue and date (Concert.FindEventsByVenueAndDate). The event collides when an Event there has the same start time (or both have none), or when the event has no start time and an Event there has one. A colliding event SHALL be staged (StagedConcert.Upsert) and not published; its resolved preview is included when its venue was looked up, and omitted when it reused the Artist's existing Event's Venue. Any other event SHALL be published under the series' Series with the Artist as performer (Concert.Create). The RejectedConcertLog SHALL NOT be consulted.

#### Scenario: Same slot as an existing event
- **WHEN** an Event at the resolved Venue, date and start time exists
- **THEN** the event is staged with its resolved preview and not published

#### Scenario: Unknown start next to a known start
- **WHEN** the event has no start time and an Event at that Venue and date starts at 18:00
- **THEN** the event is staged

#### Scenario: Known start next to an unknown-start event
- **WHEN** the event starts at 18:00 and the only Event at that Venue and date has no start time
- **THEN** a new Event starting at 18:00 is published

#### Scenario: Genuinely new
- **WHEN** no Event is at the resolved Venue and date
- **THEN** the event is published under the series' Series

### Requirement: One announcement per series

After processing a series, CreateFromDiscovered SHALL announce the new concerts to followers once, for the Artist, carrying every Event id that Concert.Create reported for that series. A series that published nothing SHALL announce nothing. A failed announcement SHALL NOT fail the batch.

#### Scenario: Three-stop tour
- **WHEN** three events of a tour are published
- **THEN** one announcement carrying the three Event ids is made

#### Scenario: Everything staged
- **WHEN** every event of a series is staged
- **THEN** no announcement is made

### Requirement: Empty new series are removed

At the end of the batch, CreateFromDiscovered SHALL remove the Series it created in this batch that have no Event and no StagedConcert (Series.DeleteOrphaned); it SHALL NOT touch other Series. A failure here SHALL NOT fail the batch.

#### Scenario: Created series left empty
- **WHEN** a Series created in this batch ended up with no Event and no StagedConcert
- **THEN** it is removed
