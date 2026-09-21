# Create From Discovered

## Purpose

Turns a discovered concert into a persisted event, grouping related tour dates into a series, deduplicating against existing records on a natural key, resolving the venue to a canonical record, and either publishing, staging for review, or skipping when the venue cannot be resolved.

## Requirements

### Requirement: Normalization in Concert Discovery Pipeline

The concert discovery pipeline SHALL normalize Gemini's free-text `admin_area` output to an ISO 3166-2 code before persisting venue data.

#### Scenario: Gemini returns recognizable admin_area

- **WHEN** the Gemini concert searcher returns a scraped event with `admin_area = "愛知県"`
- **THEN** the pipeline SHALL normalize the value to `JP-23` before creating or updating the venue record

#### Scenario: Gemini returns unrecognizable admin_area

- **WHEN** the Gemini concert searcher returns a scraped event with an unrecognizable `admin_area`
- **THEN** the pipeline SHALL set `admin_area` to NULL on the venue record

#### Scenario: Gemini prompt unchanged

- **WHEN** the Gemini concert searcher constructs its prompt
- **THEN** the prompt text and response schema SHALL remain unchanged from the current implementation
- **AND** normalization SHALL occur after parsing the Gemini response, not within the LLM interaction

### Requirement: Tour Events Group Into a Single Series

The system SHALL persist all events that Gemini grouped under one `<tour>` block as a single `Series` with `SeriesType = SERIES_TYPE_TOUR`, shared by every event in the group. This replaces the prior 1-`Series`-per-`Event` SINGLE fallback for tours.

#### Scenario: Multi-stop tour creates one TOUR series

- **WHEN** a discovered tour group contains three events at different venues/dates
- **THEN** exactly one `Series` row SHALL be created with `type = SERIES_TYPE_TOUR`
- **AND** all three `Event` rows SHALL reference that single `series_id`
- **AND** the tour title and source URL SHALL be stored once on that `Series`

#### Scenario: Single-date tour block still yields a TOUR series

- **WHEN** a `<tour>` group contains only one event within the search window
- **THEN** the created `Series` SHALL have `type = SERIES_TYPE_TOUR`
- **AND** the SeriesType SHALL NOT be downgraded based on the event count

### Requirement: Series Identity Is Adopted From Member Events

The system SHALL establish a `Series`'s cross-run identity from the events that already belong to it, not from any content-derived key. When persisting a tour group, the system SHALL reuse the `series_id` carried by the group's already-persisted events (matched by the events' physical natural key); only when no member event yet exists SHALL it mint a fresh `UUIDv7` `Series`. A `Series` SHALL have no content-derived database key and no database-level uniqueness constraint, and `series.id` SHALL be a `UUIDv7`.

#### Scenario: Re-discovery adopts the existing series

- **WHEN** a tour is discovered again on a later run and at least one of its events already exists
- **THEN** the tour group SHALL reuse the existing event's `series_id`
- **AND** no duplicate `Series` row SHALL be created

#### Scenario: A genuinely new tour mints a fresh series

- **WHEN** a tour group's events do not yet exist in the database
- **THEN** a new `Series` row SHALL be created with a `UUIDv7` identifier
- **AND** every event in the group SHALL reference that new `series_id`

#### Scenario: Divergent-title co-headline tour converges to one series

- **WHEN** the same real tour is discovered via two artists with divergent titles and no shared `source_url`
- **THEN** the second discovery's events SHALL match the first's by physical natural key
- **AND** SHALL adopt the existing `series_id`
- **AND** exactly one TOUR `Series` SHALL exist for the tour, with both artists linked via `event_performers`

### Requirement: Events Deduplicate On Physical Natural Key

The events natural key SHALL be `(venue_id, local_event_date, start_at)`, enforced as a unique constraint that treats NULL `start_at` values as equal (`NULLS NOT DISTINCT`). The key SHALL NOT include `series_id`. Two performances at the same venue and date with different start times SHALL be distinct events; two with the same venue, date, and start time SHALL be the same event regardless of which series or artist discovered them.

#### Scenario: Matinee and evening shows are distinct events

- **WHEN** two performances occur at the same venue on the same date with different `start_at` values
- **THEN** two distinct `Event` rows SHALL be persisted

#### Scenario: Same physical show discovered via two artists is one event

- **WHEN** the same `(venue_id, local_event_date, start_at)` show is discovered separately via two followed artists
- **THEN** it SHALL resolve to a single `Event` row
- **AND** both artists SHALL be linked via `event_performers`

#### Scenario: Two unpublished-time shows at one venue/date collapse

- **WHEN** two discovered events share `(venue_id, local_event_date)` and both lack a published `start_at`
- **THEN** they SHALL collapse to a single `Event` row

### Requirement: Event Identity Is Resolved In The Application

The system SHALL resolve each scraped event against existing rows before writing, so that a later-announced `start_at` updates the row first seen with a NULL start rather than inserting a duplicate, while a genuinely new start time at the same venue/date is inserted as a new event.

#### Scenario: Later-announced start time fills the existing row

- **WHEN** an event was first persisted with a NULL `start_at`
- **AND** a subsequent discovery provides a concrete `start_at` for the same `(venue_id, local_event_date)`
- **THEN** the existing row's `start_at` SHALL be filled in
- **AND** no duplicate `Event` row SHALL be created

#### Scenario: A new start time at a known venue/date is a new event

- **WHEN** an existing row at `(venue_id, local_event_date)` already has a concrete `start_at`
- **AND** a discovery provides a different concrete `start_at` for the same venue and date
- **THEN** a new `Event` row SHALL be inserted (a distinct session)

### Requirement: SeriesType Assigned From Source Classification

The system SHALL assign `SeriesType` from the Gemini block the event originated in — TOUR for `<tour>`, SINGLE for `<standalone>` — and SHALL NOT infer it from the number of events.

#### Scenario: Multi-day standalone stays SINGLE

- **WHEN** a `<standalone>` block describes a multi-day single-venue run
- **THEN** its `Series` SHALL have `type = SERIES_TYPE_SINGLE`

#### Scenario: Standalone is not grouped into a tour

- **WHEN** a `<standalone>` event shares a title with a tour
- **THEN** it SHALL NOT be folded into the tour's `Series`
- **AND** it SHALL receive its own SINGLE series

### Requirement: Multi-Hall Venues Are Disambiguated By venue_id

The system SHALL rely on `venue_id` resolution to distinguish concurrent performances in different halls of the same building. The events natural key SHALL NOT include raw venue text. When a source names the hall, distinct halls SHALL resolve to distinct `venue_id`s; when a source omits the hall, the reference MAY resolve to the building-level venue.

#### Scenario: Different halls on the same date are distinct events

- **WHEN** two performances on the same date are listed with distinct hall names of the same building (e.g. ホールA and ホールC)
- **THEN** they SHALL resolve to distinct `venue_id`s
- **AND** SHALL be persisted as two distinct `Event` rows

### Requirement: Residual Grouping Ambiguities Are Logged, Not Fatal

The system SHALL treat residual grouping ambiguities as non-fatal and SHALL log them rather than failing discovery.

#### Scenario: Late additional dates after full rotation may split

- **WHEN** a tour's previously-seen dates have all passed and been range-filtered before newly-announced dates are discovered
- **THEN** the system MAY create a second TOUR `Series` for the new dates
- **AND** discovery SHALL complete successfully without error

#### Scenario: Hall name omitted by one source may split

- **WHEN** the same physical show is discovered once with a hall name and once without
- **THEN** it MAY resolve to two `venue_id`s and two `Event` rows
- **AND** discovery SHALL complete successfully, logging the anomaly

#### Scenario: Cross-source start-time disagreement may split

- **WHEN** the same physical show is discovered via two sources that publish different concrete `start_at` values (e.g. door time vs performance time)
- **THEN** it MAY resolve to two `Event` rows under two series (a consequence of `start_at` being part of the key)
- **AND** discovery SHALL complete successfully, logging the anomaly

### Requirement: Discovery Consumer Auto-Publish, Conflict Staging, and Rejection Log

The `CONCERT.discovered` consumer SHALL resolve the venue and evaluate the
discovered concert for a same-slot conflict against the published catalog
BEFORE deciding how to persist it. When the discovered concert is genuinely
new — no existing published event at the resolved `(venue_id,
local_event_date, start_at)` (the known-start "fill" of an existing
unknown-start row counts as new, not a conflict) — the consumer SHALL publish
it directly: create or reuse the `venues` row, insert the published
`series`/`events`/`event_performers` rows (reusing the existing bulk-insert
and natural-key UPSERT behavior), and publish `CONCERT.created` so follower
notifications fire immediately; it SHALL NOT write a `pending` staged row for
a new concert. When a same-slot conflict IS detected, the consumer SHALL
instead persist a `pending` `staged_concert` row (carrying the scraped fields
and the resolved-venue preview) and SHALL NOT insert any published row or
publish `CONCERT.created`; that staged row is resolved later through the
existing approval reconciliation. A `venues` row SHALL be created only on the
auto-publish path — the conflict-staging path SHALL NOT create a new `venues`
row, because a same-slot conflict necessarily resolves to the venue of the
already-published event, so rejected or never-approved concerts SHALL NOT
create orphan `venues` rows. Auto-publish requires a resolved venue: when the
scraped venue name does NOT resolve against the venue provider, the consumer
SHALL stage the concert for review rather than auto-publishing it, and SHALL
NOT create a `venues` row — publishing a venue with no provider identity and
no coordinates would exclude the concert from proximity matching and publish
an unreviewed venue. A resolved venue is necessary but not sufficient for
auto-publish: a resolved venue that collides with an existing event is still
staged as a conflict. A concert in `pending` state SHALL NOT be returned by
any consumer-facing read RPC (`List`, `ListByFollower`,
`ListWithProximity`). The system SHALL maintain a `rejected_concerts_log`
that is append-only and used solely for searcher-quality analysis; it SHALL
NOT participate in discovery dedup or otherwise suppress future staging.

#### Scenario: Log does not affect staging

- **WHEN** the discovery pipeline evaluates whether to stage a concert
- **THEN** the presence of a matching `rejected_concerts_log` entry SHALL have no effect on the
  staging decision

#### Scenario: New concert is auto-published without staging

- **WHEN** the `CONCERT.discovered` consumer processes a discovered concert whose resolved
  `(venue_id, local_event_date, start_at)` has no existing published event
- **THEN** it SHALL create or reuse the `venues` row and insert the published event (with its
  series and performers)
- **AND** it SHALL publish `CONCERT.created`
- **AND** it SHALL NOT write a `pending` staged row

#### Scenario: Conflicting concert is staged for reconciliation

- **WHEN** the `CONCERT.discovered` consumer processes a discovered concert that maps onto an
  existing published event at the resolved `(venue_id, local_event_date, start_at)`
- **THEN** it SHALL persist a `pending` `staged_concert` row carrying the scraped fields and
  resolved-venue preview
- **AND** it SHALL NOT insert any published row and SHALL NOT publish `CONCERT.created`

#### Scenario: Known-start fill is treated as new, not a conflict

- **WHEN** a discovered concert has a known start time and the only existing published event at
  that venue and date has an unknown (NULL) start time
- **THEN** the consumer SHALL treat it as the new/publish path (filling the existing row per the
  established fill behavior) rather than staging it as a conflict

#### Scenario: Unresolved venue is staged, not auto-published

- **WHEN** the `CONCERT.discovered` consumer processes a discovered concert whose scraped venue name
  cannot be resolved against the venue provider
- **THEN** it SHALL persist a `pending` `staged_concert` row for review
- **AND** it SHALL NOT auto-publish the concert and SHALL NOT create a `venues` row

#### Scenario: Pending concerts are not fan-visible

- **WHEN** a concert is in `pending` state in the approval queue
- **THEN** it SHALL NOT be returned by any consumer-facing read RPC (`List`, `ListByFollower`,
  `ListWithProximity`)

### Requirement: Venue lookup by listed name before Places API call

The `VenueRepository` SHALL provide a `GetByListedName` method that looks up a venue by the exact `listed_venue_name` and optional `admin_area` as stored in the `venues` table. The `ConcertCreationUseCase` SHALL call this method before invoking the Google Places API during venue resolution.

#### Scenario: Venue found by listed name — API call skipped

- **WHEN** venue resolution is performed with a `listed_venue_name` and optional `admin_area`
- **AND** a venue with the same `listed_venue_name` and `admin_area` already exists in the database
- **THEN** the system SHALL return that existing venue immediately
- **AND** the system SHALL NOT call the Google Places API

#### Scenario: Venue not found by listed name — resolution continues

- **WHEN** venue resolution is performed with a `listed_venue_name` and optional `admin_area`
- **AND** no venue with that combination exists in the database
- **THEN** the system SHALL proceed to call the Google Places API as before

#### Scenario: Listed name match is case-sensitive and exact

- **WHEN** `GetByListedName` is called
- **THEN** the lookup SHALL use exact string equality on `listed_venue_name`
- **AND** variations in casing or whitespace SHALL result in a miss (falling through to the API)

### Requirement: Venue Resolution During Concert Creation

The concert creation pipeline SHALL resolve venues via a DB-first lookup before calling the Google Places API. The `placeSearcher` dependency remains required (not optional). When a venue is found by listed name in the database, the Places API SHALL NOT be called.

#### Scenario: Venue found by listed name in DB — API skipped

- **WHEN** the concert creation pipeline processes a scraped concert
- **AND** a venue with the same `listed_venue_name` and `admin_area` already exists in the database
- **THEN** the system SHALL return that existing venue immediately
- **AND** the system SHALL NOT call the Google Places API

#### Scenario: Venue found by listed name in batch-local cache — API skipped

- **WHEN** the concert creation pipeline processes a scraped concert
- **AND** the venue's `listed_venue_name` matches a venue already resolved in the current batch (via `newVenues` map keyed by `listed_venue_name`)
- **THEN** the cached venue SHALL be reused without additional database or API calls

#### Scenario: Venue not in DB — Places API called

- **WHEN** the concert creation pipeline processes a scraped concert
- **AND** no venue with the same `listed_venue_name` and `admin_area` exists in the database
- **THEN** the system SHALL call the Google Places API to obtain a canonical `google_place_id`
- **AND** proceed with the existing `GetByPlaceID` → create flow

#### Scenario: Successful venue resolution via Places API

- **WHEN** the concert creation pipeline processes a scraped concert
- **AND** no DB match was found for the listed name
- **AND** Google Places API returns a match
- **THEN** the system SHALL look up an existing venue by `google_place_id` via `GetByPlaceID`
- **AND** if no existing venue is found, the system SHALL create a new venue with canonical name, coordinates, and `google_place_id` from the Places API result

#### Scenario: Venue already exists by place_id

- **WHEN** the concert creation pipeline processes a scraped concert
- **AND** no DB match was found for the listed name
- **AND** Google Places API returns a match
- **AND** a venue with the same `google_place_id` already exists in the database
- **THEN** the existing venue SHALL be reused (no new venue created)

### Requirement: Skip Unresolvable Venues

The concert creation pipeline SHALL skip concerts whose venues cannot be resolved via Google Places API, rather than creating venue records with incomplete data.

#### Scenario: Places API returns NotFound

- **WHEN** `resolveVenue` calls Google Places API for a scraped venue name
- **AND** the API returns NotFound
- **THEN** the concert SHALL NOT be persisted to the database
- **AND** the system SHALL emit a structured Warn log containing all fields of the `ScrapedConcert` (title, local_date, start_time, open_time, listed_venue_name, admin_area, source_url)
- **AND** processing SHALL continue with the next concert in the batch

#### Scenario: Places API returns a non-retryable error

- **WHEN** `resolveVenue` calls Google Places API for a scraped venue name
- **AND** the API returns an error that is not NotFound (e.g., InvalidArgument)
- **THEN** the concert SHALL NOT be persisted to the database
- **AND** the system SHALL emit a structured Warn log with the error and all `ScrapedConcert` fields
- **AND** processing SHALL continue with the next concert in the batch

### Requirement: Google Places API Request Includes Language Code

When the concert creation pipeline calls Google Places `SearchPlace`, the request SHALL include a `languageCode` field derived from the venue's country code. The country code SHALL be extracted from the ISO 3166-2 `admin_area` field (e.g., `"JP-13"` → `"JP"`). The mapping from country code to BCP 47 language tag SHALL follow a static lookup table with `"en"` as the default.

#### Scenario: Japanese venue resolves with Japanese language code

- **WHEN** the concert creation pipeline calls `SearchPlace` for a venue with `admin_area` starting with `"JP"`
- **THEN** the Places API request SHALL include `languageCode: "ja"`
- **AND** the returned canonical `venue.name` SHALL be in Japanese when available

#### Scenario: Korean venue resolves with Korean language code

- **WHEN** the concert creation pipeline calls `SearchPlace` for a venue with `admin_area` starting with `"KR"`
- **THEN** the Places API request SHALL include `languageCode: "ko"`

#### Scenario: Unknown country defaults to English language code

- **WHEN** the concert creation pipeline calls `SearchPlace` for a venue whose country code is not in the static mapping
- **THEN** the Places API request SHALL include `languageCode: "en"`

#### Scenario: Absent admin_area defaults to English language code

- **WHEN** the concert creation pipeline calls `SearchPlace` for a venue with no `admin_area`
- **THEN** the Places API request SHALL include `languageCode: "en"`

### Requirement: listed_venue_name Is Normalized Before Storage

The concert creation pipeline SHALL apply `NormalizeVenueName` to the scraped `listed_venue_name` before storing it in the `staged_concerts` row. The raw (unnormalized) value SHALL NOT be persisted.

#### Scenario: Prefecture prefix stripped before storage

- **WHEN** the concert creation pipeline processes a scraped concert with `listed_venue_name` equal to `"大阪・フェスティバルホール"`
- **THEN** the stored `listed_venue_name` SHALL be `"フェスティバルホール"`

#### Scenario: Whitespace-only listed_venue_name is rejected

- **WHEN** `NormalizeVenueName` reduces the scraped venue name to an empty string after normalization
- **THEN** the concert SHALL be treated the same as having a missing `listed_venue_name`

#### Scenario: Already-normalized name is stored unchanged

- **WHEN** the concert creation pipeline processes a scraped concert with `listed_venue_name` equal to `"日本武道館"`
- **THEN** the stored `listed_venue_name` SHALL be `"日本武道館"` (unchanged, normalization is idempotent)
