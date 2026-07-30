# venue-normalization Specification

## Purpose

The Venue Normalization capability resolves scraped venue names to canonical venue records via Google Places API during concert creation. Venues are either resolved to a canonical record (with name, coordinates, and `google_place_id`) or the concert is skipped with structured logging.
## Requirements
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

### Requirement: PlaceSearcher Is Required

The `ConcertCreationUseCase` SHALL require a non-nil `VenuePlaceSearcher` at construction time.

#### Scenario: Nil placeSearcher at startup

- **WHEN** `NewConcertCreationUseCase` is called with a nil `placeSearcher`
- **THEN** the function SHALL panic with a descriptive message

### Requirement: Idempotent venue get-or-create with place_id-authoritative identity

The venue lookup-or-create path SHALL be idempotent and SHALL NOT fail when a venue
matching the resolved identity already exists. This path runs only when a staged concert is
approved (the sole caller that creates a `venues` row), and it supersedes the insert-only
create step described by the "Venue Resolution During Concert Creation" requirement. Identity
SHALL be resolved in this order:
(1) by `google_place_id` when the staged/scraped concert carries one; (2) on miss, by
`(listed_venue_name, admin_area)`; (3) only when neither matches SHALL a new `venues`
row be created. Creation SHALL use `INSERT … ON CONFLICT DO NOTHING` (untargeted, so a
violation on either the `google_place_id` partial-unique index or the
`(listed_venue_name, admin_area)` partial-unique index is absorbed) followed by a
re-SELECT on the same keys, so a lost race or a divergent identity resolves to the
existing row rather than surfacing an `already_exists` error.

The `admin_area` used for the `(listed_venue_name, admin_area)` fallback lookup and the
`admin_area` written on insert SHALL be derived identically (the resolved admin_area when
present, otherwise the raw scraped admin_area), so the read key and the write key never
diverge.

When the fallback lookup finds a venue whose `google_place_id` is NULL and the incoming
concert carries a resolved `google_place_id`, the system MAY backfill that value; it
SHALL NEVER overwrite an existing non-NULL `google_place_id`.

#### Scenario: No existing venue — a new row is created

- **WHEN** neither `google_place_id` nor `(listed_venue_name, admin_area)` matches an
  existing venue
- **THEN** the system SHALL insert a new `venues` row for the resolved identity
- **AND** SHALL return the newly created venue id

#### Scenario: Existing venue found by place_id

- **WHEN** a venue with the resolved `google_place_id` already exists
- **THEN** the system SHALL return that venue
- **AND** SHALL NOT attempt an insert

#### Scenario: place_id miss falls back to listed name and admin_area

- **WHEN** the resolved `google_place_id` does not match any existing venue
- **AND** a venue with the same `(listed_venue_name, admin_area)` already exists (with a
  different or NULL `google_place_id`)
- **THEN** the system SHALL return that existing venue
- **AND** SHALL NOT attempt to insert a new venue row
- **AND** SHALL NOT raise `already_exists`

#### Scenario: Concurrent create resolves to a single row

- **WHEN** two approvals resolve the same venue identity concurrently and both reach the
  insert step
- **THEN** the `ON CONFLICT DO NOTHING` insert SHALL suppress the losing insert
- **AND** the losing path SHALL re-SELECT by `google_place_id` then by
  `(listed_venue_name, admin_area)` and return the surviving row

#### Scenario: Fallback lookup and insert use the same admin_area

- **WHEN** a concert has a raw `admin_area` and no resolved `admin_area`
- **THEN** the fallback lookup and any subsequent insert SHALL both use the raw
  `admin_area`
- **AND** the lookup SHALL therefore match a row the insert would have collided with

#### Scenario: NULL place_id backfilled, non-NULL never overwritten

- **WHEN** the fallback finds an existing venue whose `google_place_id` is NULL
- **AND** the incoming concert carries a resolved `google_place_id`
- **THEN** the system MAY set the existing row's `google_place_id` to the resolved value
- **WHEN** the existing venue already has a non-NULL `google_place_id`
- **THEN** the system SHALL leave it unchanged

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

