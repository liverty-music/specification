# Concert

## Purpose

Defines the Concert entity as a scheduled performance extending a single event, embedding its resolved venue, series, and performers, tracking when it was last searched, and classifying its proximity to a user's home.

## Requirements

### Requirement: Concert-Event Association

Every Concert entity SHALL be securely linked to a distinct generic Event entity.

#### Scenario: Concert Data Integrity
- **WHEN** a Concert is persisted or retrieved
- **THEN** it MUST include all fields defined in the `Event` entity (Title, Date, Venue, etc.)
- **AND** data consistency between the Concert specific fields (ArtistID) and Event generic fields MUST be maintained

### Requirement: Discovered-concert deduplication by date

Newly discovered (scraped) concerts SHALL be deduplicated against a set of existing concerts using date-only comparison: a discovered concert is considered a duplicate if its local event date matches the local event date of an existing concert, or the local event date of an earlier discovered concert already kept from the same batch. Discovered concerts SHALL be evaluated in their original order, and only concerts whose date does not conflict SHALL be kept, in that same order. This deduplication SHALL apply both across batches (against previously known concerts) and within a single batch (concerts discovered together).

#### Scenario: Empty scraped list

- **WHEN** the discovered-concerts list is empty and the existing concerts are any value
- **THEN** no concerts SHALL be kept

#### Scenario: No existing concerts

- **WHEN** there are no existing concerts and the discovered concerts have different dates
- **THEN** all discovered concerts SHALL be kept

#### Scenario: All scraped concerts conflict with existing

- **WHEN** every discovered concert's date matches an existing concert's date
- **THEN** no discovered concerts SHALL be kept

#### Scenario: Partial overlap with existing

- **WHEN** 3 concerts are discovered, 1 conflicts with an existing concert and 2 do not
- **THEN** the 2 non-conflicting concerts SHALL be kept, in their original order

#### Scenario: Within-batch duplicate on same date

- **WHEN** 2 discovered concerts share the same date and no existing concert has that date
- **THEN** only the first of the two SHALL be kept (within-batch dedup)

#### Scenario: Within-batch duplicate conflicts with existing

- **WHEN** 2 discovered concerts share the same date, and that date also matches an existing concert
- **THEN** neither discovered concert SHALL be kept

#### Scenario: Preserves original order

- **WHEN** discovered concerts have dates in the order [Mar 15, Mar 17, Mar 16] and none conflict
- **THEN** they SHALL be kept in that same order [Mar 15, Mar 17, Mar 16]

#### Scenario: Nil existing concerts

- **WHEN** there is no record of existing concerts and concerts have been discovered
- **THEN** all discovered concerts SHALL be kept (there is nothing to conflict with)

### Requirement: Discovered-concert JSON payload encoding

The discovered-concert entity SHALL have JSON tags on all fields to support serialization as an event payload.

Field-to-JSON-tag mapping:
- `Title` → `"title"`
- `ListedVenueName` → `"listed_venue_name"`
- `AdminArea` → `"admin_area,omitempty"`
- `LocalDate` → `"local_date"`
- `StartTime` → `"start_time,omitempty"`
- `OpenTime` → `"open_time,omitempty"`
- `SourceURL` → `"source_url"`

#### Scenario: Marshal omits nil optional fields

- **WHEN** a discovered-concert entity with `AdminArea=nil`, `StartTime=nil`, `OpenTime=nil` is marshaled to JSON
- **THEN** the JSON output does not contain `"admin_area"`, `"start_time"`, or `"open_time"` keys

#### Scenario: Marshal includes all non-nil fields

- **WHEN** a discovered-concert entity with all fields set is marshaled to JSON
- **THEN** all 7 fields appear in the JSON output with correct key names

### Requirement: Discovered-concert to Concert conversion

The discovered-concert entity SHALL provide a `ToConcert(artistID, eventID, venueID string) *Concert` method that constructs a `Concert` from the scraped data.

The method SHALL map fields as follows:
- `Concert.ID` = `eventID`
- `Concert.ArtistID` = `artistID`
- `Concert.VenueID` = `venueID`
- `Concert.Title` = the discovered-concert entity's `Title`
- `Concert.LocalDate` = the discovered-concert entity's `LocalDate`
- `Concert.StartTime` = the discovered-concert entity's `StartTime`
- `Concert.URL` = the discovered-concert entity's `URL`

#### Scenario: Full field mapping

- **WHEN** `ToConcert` is called on a discovered-concert entity with all fields populated
- **THEN** the returned `Concert` has ID=eventID, ArtistID=artistID, VenueID=venueID, and all other fields copied from the discovered-concert entity

#### Scenario: Nil optional fields

- **WHEN** `ToConcert` is called on a discovered-concert entity where StartTime and URL are nil
- **THEN** the returned `Concert` has nil StartTime and nil URL

#### Scenario: Multiple calls produce distinct concerts

- **WHEN** `ToConcert` is called twice with different artistID/eventID/venueID values on the same discovered-concert entity
- **THEN** each call returns a distinct `Concert` with the respective IDs

### Requirement: SearchLog freshness check

The `SearchLog` entity SHALL provide an `IsFresh(now time.Time, ttl time.Duration) bool` method that determines whether a search log entry is still fresh.

The method SHALL return true when:
1. The search log has a completed status, AND
2. The time elapsed since the search log's completion timestamp is less than `ttl`.

#### Scenario: Fresh completed log

- **WHEN** IsFresh is called with now=14:00, ttl=1h, and the SearchLog completed at 13:30
- **THEN** returns true (30 minutes < 1 hour)

#### Scenario: Stale completed log

- **WHEN** IsFresh is called with now=16:00, ttl=1h, and the SearchLog completed at 13:30
- **THEN** returns false (2.5 hours > 1 hour)

#### Scenario: Non-completed log

- **WHEN** IsFresh is called on a SearchLog with pending status
- **THEN** returns false (not completed)

---

### Requirement: SearchLog pending check

The `SearchLog` entity SHALL provide an `IsPending(now time.Time, timeout time.Duration) bool` method that determines whether a search log entry is still actively pending (not timed out).

The method SHALL return true when:
1. The search log has a pending status, AND
2. The time elapsed since the search log's creation timestamp is less than `timeout`.

#### Scenario: Active pending log

- **WHEN** IsPending is called with now=14:00, timeout=5m, and the SearchLog was created at 13:57
- **THEN** returns true (3 minutes < 5 minutes)

#### Scenario: Timed-out pending log

- **WHEN** IsPending is called with now=14:10, timeout=5m, and the SearchLog was created at 13:57
- **THEN** returns false (13 minutes > 5 minutes)

#### Scenario: Completed log is not pending

- **WHEN** IsPending is called on a SearchLog with completed status
- **THEN** returns false (not pending)

---

### Requirement: Concert extends Event via a 1:1 relationship

The system SHALL support extending the base `Event` entity with domain-specific entities (e.g., `Concert`) via a 1:1 relationship. The domain-specific extension table MAY exist as a placeholder for future specialised columns, even when it currently carries no additional fields.

#### Scenario: Concert as Event

- **WHEN** a `Concert` is created
- **THEN** an associated `Event` record is strictly required
- **AND** the `Concert` record shares the same unique identifier (or references it as a foreign key with uniqueness constraint)

#### Scenario: Music-specific extension placeholder is retained

- **WHEN** the `concerts` table contains no music-specific columns beyond `event_id`
- **THEN** the table SHALL still be retained as a placeholder for future music-specific extensions
- **AND** the `Concert` proto message SHALL continue to exist as the user-facing DTO for music events

### Requirement: Concert embeds resolved series and performers

The `Concert` proto message SHALL embed the full `Series` parent and SHALL expose performing artists via `repeated Artist performers`, so that a single RPC response carries all data needed to render the event to a user.

The `Concert` message SHALL NOT contain `Title title` or `Url source_url` fields; those values SHALL be accessed through the embedded `Series`.

The `Concert` message MAY retain `VenueId venue_id` alongside the embedded `Venue venue` field as a backward-compatibility convenience for clients that have not yet migrated to reading `venue.id`. The proto comment on `venue_id` SHALL flag the field as legacy ("prefer the embedded `venue` field"), and a future change SHOULD migrate consumers off it and reserve the field number.

#### Scenario: Concert response carries embedded Series

- **WHEN** a `Concert` is returned from any RPC
- **THEN** the `series` field SHALL contain the full `Series` message (not just a `SeriesId`)
- **AND** the client SHALL be able to render the concert without issuing a follow-up call to fetch the `Series`

#### Scenario: Concert response carries all performers

- **WHEN** a `Concert` is returned from any RPC
- **THEN** the `performers` repeated field SHALL contain at least one `Artist`
- **AND** all artists associated with the underlying `Event` via `event_performers` SHALL be present in the response

#### Scenario: Concert does not duplicate series-level metadata

- **WHEN** the `Concert` proto message is defined
- **THEN** it SHALL NOT contain a `Title title` field
- **AND** it SHALL NOT contain a `Url source_url` field

### Requirement: Concert schedule data model

The system SHALL define standard data structures for core concert entities to ensure consistency across services.

#### Scenario: Artist Definition

- **WHEN** an artist is represented
- **THEN** it SHALL include a unique ID, name, and a list of official media channels.

#### Scenario: Venue Definition

- **WHEN** a venue is represented
- **THEN** it SHALL include a unique ID and name.
- **AND** it MAY include an administrative area (`admin_area`) as an ISO 3166-2 subdivision code representing the venue's geographic administrative division (e.g., `JP-13` for Tokyo, `JP-40` for Fukuoka).

#### Scenario: Concert Definition

- **WHEN** a concert is represented
- **THEN** it SHALL include the artist ID, venue ID, local date (`local_date`), title, and start time.
- **AND** it MAY include open time, source URL, listed venue name, and an embedded `Venue` object.
- **AND** all primitive scalar fields (date, time, title, URL, venue name) SHALL be represented as VO wrapper messages.

#### Scenario: Event Definition

- **WHEN** an event is represented
- **THEN** it SHALL include a unique ID, an embedded `Venue` object, title, and local date.
- **AND** it MAY include start time and open time.
- **AND** all primitive scalar fields SHALL be represented as VO wrapper messages.
- **AND** it SHALL NOT include `create_time` or `update_time` fields.

#### Scenario: Concert card displays ticket journey badge

- **WHEN** a concert is rendered on the dashboard
- **AND** the user has a ticket journey for that concert's event
- **THEN** the concert card SHALL display a badge indicating the current `TicketJourneyStatus`

#### Scenario: Concert card without ticket journey

- **WHEN** a concert is rendered on the dashboard
- **AND** the user has no ticket journey for that concert's event
- **THEN** the concert card SHALL NOT display a journey status badge

### Requirement: Proto Value Object Consistency

All primitive scalar fields on `Concert` and `Event` proto messages SHALL use VO wrapper messages to carry validation constraints and semantic meaning, matching the Go entity layer conventions.

#### Scenario: LocalDate VO

- **WHEN** a calendar date is represented in `Concert` or `Event`
- **THEN** it SHALL use the `LocalDate` wrapper message containing a `google.type.Date` value.
- **AND** the field SHALL be named `local_date`.

#### Scenario: StartTime and OpenTime VOs

- **WHEN** a start or open time is represented in `Concert` or `Event`
- **THEN** it SHALL use `StartTime` or `OpenTime` wrapper messages containing a `google.protobuf.Timestamp` value.

#### Scenario: Title VO

- **WHEN** a title is represented in `Concert` or `Event`
- **THEN** it SHALL use the `Title` wrapper message containing a non-empty string value.

#### Scenario: SourceUrl VO

- **WHEN** a source URL is represented in `Concert`
- **THEN** it SHALL use the `SourceUrl` wrapper message containing a URI-validated string value.

#### Scenario: ListedVenueName VO

- **WHEN** a raw scraped venue name is represented in `Concert`
- **THEN** it SHALL use the `ListedVenueName` wrapper message containing a string value.

### Requirement: Concert carries an embedded venue

Both `Concert` and `Event` proto messages SHALL embed a resolved `Venue` object populated by the server, rather than relying solely on a `venue_id` reference.

#### Scenario: Concert carries embedded Venue

- **WHEN** a `Concert` is returned from any RPC
- **THEN** the `venue` field SHALL be populated with the corresponding `Venue` entity including `name` and `admin_area` if available.

#### Scenario: Event carries embedded Venue

- **WHEN** an `Event` is returned from any RPC
- **THEN** the `venue` field SHALL be populated with the corresponding `Venue` entity.

### Requirement: Concert classifies its proximity to a user's home

The Go entity layer SHALL provide a `ProximityTo` receiver method on `Concert` that classifies the geographic relationship between the concert's venue and a user's home. This method SHALL be a pure function over entity fields with no infrastructure dependencies.

#### Scenario: HOME classification by admin_area match

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the concert's venue `admin_area` matches `home.Level1`
- **THEN** the method SHALL return `ProximityHome`

#### Scenario: NEARBY classification by Haversine distance

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the venue's `admin_area` does not match `home.Level1`
- **AND** the venue has latitude and longitude coordinates
- **AND** the Haversine distance between `(home.Latitude, home.Longitude)` and the venue coordinates is less than or equal to 200km
- **THEN** the method SHALL return `ProximityNearby`

#### Scenario: AWAY classification for distant venues

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the Haversine distance exceeds 200km
- **THEN** the method SHALL return `ProximityAway`

#### Scenario: AWAY classification when venue has no coordinates

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the venue's latitude or longitude is nil
- **THEN** the method SHALL return `ProximityAway`

#### Scenario: AWAY classification when home is nil

- **WHEN** `Concert.ProximityTo(nil)` is called
- **THEN** the method SHALL return `ProximityAway`

#### Scenario: AWAY classification when venue is nil

- **WHEN** `Concert.ProximityTo(home)` is called
- **AND** the concert's venue is nil
- **THEN** the method SHALL return `ProximityAway`
