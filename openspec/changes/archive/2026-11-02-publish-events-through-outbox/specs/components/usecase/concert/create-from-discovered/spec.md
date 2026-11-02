## ADDED Requirements

### Requirement: Runs when a search starts it

CreateFromDiscovered SHALL run when ConcertUseCase.SearchNewConcerts starts it for an Artist's search, with that Artist and the DiscoveredSeries the search kept. It SHALL be named after the Artist and the search time of the Artist's ConcertSearch, so one search starts it once. When it fails, the same DiscoveredSeries SHALL be processed again; every step SHALL be safe to repeat.

#### Scenario: Search keeps new concerts
- **WHEN** SearchNewConcerts keeps a tour and a standalone show for an Artist
- **THEN** CreateFromDiscovered runs once for that Artist with both series

#### Scenario: Processed again after a failure
- **WHEN** a batch that was already fully processed is processed again
- **THEN** no Event, Series or ConcertCandidate is added a second time

### Requirement: The published events of a series are created together

For each series, CreateFromDiscovered SHALL publish every event it decides to publish in one Concert.Create call under the series' Series with the Artist as performer, after deciding for each event of the series whether to publish, stage, fill or skip it. Concert.Create then tells the Artist's followers about them once. A series that publishes nothing SHALL NOT call Concert.Create. When Concert.Create fails, the batch SHALL fail.

#### Scenario: Three-stop tour
- **WHEN** three events of a tour are to be published
- **THEN** Concert.Create is called once with the three events

#### Scenario: Everything staged
- **WHEN** every event of a series is staged
- **THEN** Concert.Create is not called for that series

#### Scenario: Concerts cannot be created
- **WHEN** Concert.Create fails with Unavailable for a series
- **THEN** CreateFromDiscovered fails and the batch is processed again later

## MODIFIED Requirements

### Requirement: Collision is staged, anything else is published

For a resolved, unsuppressed event, CreateFromDiscovered SHALL look up the Events at its Venue and date (Concert.FindEventsByVenueAndDate). The event collides when an Event there has the same start time (or both have none), or when the event has no start time and an Event there has one. A colliding event SHALL be staged (ConcertCandidate.Upsert) and not published; its resolved preview is included when its venue was looked up, and omitted when it reused the Artist's existing Event's Venue. Any other event SHALL be published under the series' Series with the Artist as performer, together with the series' other published events (see "The published events of a series are created together"). The RejectedConcert SHALL NOT be consulted.

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

## REMOVED Requirements

### Requirement: Triggered by a discovery announcement
**Reason**: Found concerts are a request for one receiver, not an announcement: ConcertUseCase.SearchNewConcerts starts CreateFromDiscovered directly.
**Migration**: Replaced by "Runs when a search starts it".

### Requirement: One announcement per series
**Reason**: Concert.Create announces the new concerts together with the Events it stores (components/entity/concert/create), so CreateFromDiscovered no longer announces. To keep one notification per series for each follower, the published events of a series are stored in one Concert.Create call.
**Migration**: Replaced by "The published events of a series are created together". A failure to announce now fails Concert.Create, so the batch fails and is processed again, instead of the Events being stored without telling followers.
