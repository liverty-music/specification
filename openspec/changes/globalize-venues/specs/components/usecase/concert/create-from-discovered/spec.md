## MODIFIED Requirements

### Requirement: Venue resolution

For any other event that has an admin area and a time zone, CreateFromDiscovered SHALL look up the places for the venue's listed name and admin area (Venue.SearchPlace), at most once per name and admin area within the batch, and choose one with Venue.SelectPlace: the first place whose canonical name is the same listed venue as the listed name, otherwise the most relevant. When a place is chosen, the Venue SHALL be found or created in this order: by place id (Venue.GetByPlaceID); by listed venue name and admin area (Venue.GetByListedName), giving that Venue the place id when it has none (Venue.BackfillPlaceID); otherwise created (Venue.Create) named by the listed venue name, with the place id, the place's coordinates with the time they were read, the listed venue name, the discovered admin area and the discovered time zone. The place's canonical name SHALL be used only to choose the place and SHALL NOT be stored. Any lookup failure other than no match SHALL fail the whole batch.

#### Scenario: Known place
- **WHEN** the place is found and a Venue holds its place id
- **THEN** that Venue is used and no Venue is created

#### Scenario: Place id differs from the stored venue
- **WHEN** the place's id matches no Venue but a Venue holds the listed venue name and admin area without a place id
- **THEN** that Venue is used and takes the place id

#### Scenario: New venue takes the listed name
- **WHEN** an event lists "Zepp Haneda(TOKYO)" in JP-13 with time zone Asia/Tokyo, the chosen place is named "Zepp Haneda (TOKYO)" and no Venue holds it
- **THEN** a Venue named "Zepp Haneda(TOKYO)" is created with the place id, the place's coordinates and their fetch time, JP-13 and Asia/Tokyo

#### Scenario: New overseas venue
- **WHEN** an event in Bordeaux comes with the admin area FR-NAQ and the time zone Europe/Paris, and no Venue holds the place found for it
- **THEN** a Venue is created with the admin area FR-NAQ and the time zone Europe/Paris

#### Scenario: Catalog unavailable
- **WHEN** the venue lookup fails with Unavailable
- **THEN** CreateFromDiscovered fails and the discovery is processed again later

### Requirement: Unresolved venue is staged

When the event has no admin area or no time zone, CreateFromDiscovered SHALL stage it (ConcertCandidate.Upsert) without looking up the venue. When the venue lookup chooses no place (the search finds none, or none inside the event's admin area, see Venue.SelectPlace), it SHALL stage the event without a resolved place id. In both cases it SHALL NOT create a Venue and SHALL NOT publish the event.

#### Scenario: Venue not found
- **WHEN** no place is chosen
- **THEN** a ConcertCandidate without a resolved place id is stored and nothing is published

#### Scenario: Only places elsewhere
- **WHEN** an event's admin area is US-CA and every place found for its venue lies in another country or admin area
- **THEN** a ConcertCandidate without a resolved place id is stored, no Venue is created and nothing is published

#### Scenario: Area unknown
- **WHEN** an event comes without an admin area
- **THEN** the venue is not looked up, a ConcertCandidate without an admin area and without a resolved place id is stored, and nothing is published

#### Scenario: Time zone unknown
- **WHEN** an event comes with the admin area US-TX and no time zone
- **THEN** the venue is not looked up, a ConcertCandidate with US-TX, without a time zone and without a resolved place id is stored, and nothing is published

### Requirement: Collision is staged, anything else is published

For a resolved event, CreateFromDiscovered SHALL look up the Events at its Venue and date (Concert.FindEventsByVenueAndDate). The event collides when an Event there has the same start time (or both have none), or when the event has no start time and an Event there has one. A colliding event SHALL be staged (ConcertCandidate.Upsert) and not published; it carries the resolved place id when its venue was looked up, and none when it reused the Artist's existing Event's Venue. Any other event SHALL be published under the series' Series with the Artist as performer, together with the series' other published events (see "The published events of a series are created together"). The RejectedConcert SHALL NOT be consulted.

#### Scenario: Same slot as an existing event
- **WHEN** an Event at the resolved Venue, date and start time exists
- **THEN** the event is staged with its resolved place id and not published

#### Scenario: Unknown start next to a known start
- **WHEN** the event has no start time and an Event at that Venue and date starts at 18:00
- **THEN** the event is staged

#### Scenario: Known start next to an unknown-start event
- **WHEN** the event starts at 18:00 and the only Event at that Venue and date has no start time
- **THEN** a new Event starting at 18:00 is published

#### Scenario: Genuinely new
- **WHEN** no Event is at the resolved Venue and date
- **THEN** the event is published under the series' Series

## ADDED Requirements

### Requirement: What a staged event carries

A ConcertCandidate staged by CreateFromDiscovered SHALL carry the event's listed venue name, its admin area and time zone when discovery found them, its start and open times as times of day at the venue as the source stated them, and the resolved place id when a place was chosen. It SHALL NOT carry a venue name or coordinates read from the map catalog.

#### Scenario: Staged collision with a resolved place
- **WHEN** an event in JP-13 with time zone Asia/Tokyo, starting at 18:00, collides after its venue was resolved to place P named "Zepp Haneda (TOKYO)" by the map catalog
- **THEN** the ConcertCandidate carries the listed venue name, JP-13, Asia/Tokyo, the start time 18:00 and the resolved place id P, and no name or coordinates from the map catalog
