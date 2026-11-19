## REMOVED Requirements

### Requirement: Suppressed slot is skipped
**Reason**: Suppression is retired: an admin deletes a Concert only to clean up test data of Artists that discovery never searches, so a deleted slot needs no protection, and a suppressed slot could hide a real concert.
**Migration**: A discovered event at a slot where a Concert was deleted is published or staged like any other.

## MODIFIED Requirements

### Requirement: Collision is staged, anything else is published

For a resolved event, CreateFromDiscovered SHALL look up the Events at its Venue and date (Concert.FindEventsByVenueAndDate). The event collides when an Event there has the same start time (or both have none), or when the event has no start time and an Event there has one. A colliding event SHALL be staged (ConcertCandidate.Upsert) and not published; its resolved preview is included when its venue was looked up, and omitted when it reused the Artist's existing Event's Venue. Any other event SHALL be published under the series' Series with the Artist as performer, together with the series' other published events (see "The published events of a series are created together"). The RejectedConcert SHALL NOT be consulted.

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

### Requirement: Each batch reports what it did

At the end of a batch, whether it completed or failed, CreateFromDiscovered SHALL send one "concert ingest completed" signal for product analytics, under the trace of the discovery it handles, carrying the Artist, whether the batch completed or failed, and the numbers of events it published, staged for review, filled in on an existing Event and kept as conflicts. A failed batch reports what it had done before failing; each redelivery of a failed batch is a batch of its own. A failure to send it SHALL NOT change the batch.

#### Scenario: Mixed batch
- **WHEN** a batch publishes 3 events and stages 1 for review
- **THEN** one signal is sent with 3 published and 1 staged, in the same trace as the search that found them

#### Scenario: Batch fails part way
- **WHEN** a batch publishes 2 events and then fails on the next series
- **THEN** one signal is sent stating the batch failed, with 2 published, and the batch still fails
