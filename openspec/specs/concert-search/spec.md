# Capability: Concert Search

## Purpose

To define the interface and behavior for discovering new concerts for artists, enabling the system to keep its concert catalog up-to-date.

## Requirements

### Requirement: Search Concerts by Artist

System must provide a way to search for future concerts of a specific artist using generative AI grounding. The system SHALL check the search log before calling the external API and skip the call if a recent search exists. The extracted concert data SHALL include the venue's administrative area (`admin_area`) when it can be determined with confidence. The `SearchNewConcerts` RPC SHALL be accessible without authentication to support guest onboarding flows.

#### Scenario: Successful Search

- **WHEN** `SearchNewConcerts` is called for an existing artist
- **AND** no search log exists or the last search was more than 24 hours ago
- **THEN** the system MUST call the external search API
- **AND** return a list of upcoming concerts found on the web
- **AND** each concert includes title, listed venue name, date, and optionally start time and `admin_area`
- **AND** results exclude concerts that are already stored in the database

#### Scenario: Skip search when recently searched

- **WHEN** `SearchNewConcerts` is called for an artist
- **AND** a search log exists with `searched_at` within the last 24 hours
- **THEN** the system MUST NOT call the external search API
- **AND** return an empty list

#### Scenario: Filter Past Events

- **WHEN** the search results include events with dates in the past
- **THEN** the system MUST filter them out and only return future events

#### Scenario: No Results

- **WHEN** no upcoming concerts are found for the artist
- **THEN** the system MUST return an empty list without error

#### Scenario: Missing Artist ID

- **WHEN** an `artist_id` is not provided
- **THEN** the system MUST return an `INVALID_ARGUMENT` error

#### Scenario: Unauthenticated access

- **WHEN** `SearchNewConcerts` is called without a bearer token
- **THEN** the system SHALL process the request normally (public procedure)
- **AND** the search log cache SHALL prevent abuse by skipping external API calls for recently searched artists

### Requirement: Venue Administrative Area Extraction

The Gemini extraction pipeline SHALL attempt to identify the administrative area (都道府県 / state / province) of each venue. Accuracy is prioritized over coverage — an incorrect value is strictly forbidden.

#### Scenario: AdminArea explicitly stated in source

- **WHEN** the source page or venue name explicitly includes the prefecture or state
- **THEN** the extracted `admin_area` SHALL contain that value (e.g., `"大阪府"`, `"California"`)

#### Scenario: AdminArea unambiguously inferable from venue name

- **WHEN** the venue name unambiguously implies a known administrative area (e.g., "Zepp Nagoya" → "愛知県", "札幌ドーム" → "北海道")
- **THEN** the extracted `admin_area` SHALL contain the inferred value

#### Scenario: AdminArea uncertain or ambiguous

- **WHEN** the administrative area cannot be determined with confidence from the source text
- **THEN** `admin_area` SHALL be omitted (empty string / `NULL`)
- **AND** the system SHALL NOT guess or infer from partial information

### Requirement: Resilient External Search

The system SHALL retry transient failures from the external search API using exponential backoff before reporting an error. The `SearchNewConcerts` RPC SHALL have a dedicated timeout (≥15 seconds) independent of the global handler timeout to accommodate the latency of AI-grounded search.

#### Scenario: Transient Gemini timeout is retried

- **WHEN** `SearchNewConcerts` calls the external search API
- **AND** the API returns a transient error (504 Gateway Timeout, 503 Unavailable, 429 Too Many Requests, or 499 Client Cancelled)
- **THEN** the system MUST retry the call up to 2 additional times with exponential backoff
- **AND** return results if any retry succeeds

#### Scenario: All retries exhausted

- **WHEN** `SearchNewConcerts` calls the external search API
- **AND** all retry attempts fail with transient errors
- **THEN** the system MUST return an error to the caller
- **AND** log each failed attempt with the error details

#### Scenario: Non-transient error is not retried

- **WHEN** `SearchNewConcerts` calls the external search API
- **AND** the API returns a non-transient error (400 Bad Request, 401 Unauthorized)
- **THEN** the system MUST NOT retry the call
- **AND** return the error immediately

#### Scenario: Response truncated by token limit

- **WHEN** the external search API returns a response with `FinishReason = MAX_TOKENS`
- **THEN** the system MUST return an error without attempting to parse the partial JSON
- **AND** log the truncation with token usage details

#### Scenario: Literal "null" string in optional time fields

- **WHEN** the external search API returns the literal string `"null"` for `start_time` or `open_time` (due to the schema type not supporting JSON null)
- **THEN** the system MUST treat the value as absent (nil) rather than a parse error

### Requirement: Concert Deduplication Natural Key

The `executeSearch` dedup logic SHALL use the natural key `(local_event_date, listed_venue_name, start_at_utc)` to determine whether a scraped concert already exists in the database. The comparison SHALL normalize timezone differences and handle `start_at` nil states according to the rules defined below. The dedup SHALL apply both when comparing scraped concerts against existing DB records and when comparing scraped concerts within the same batch.

#### Scenario: Same instant expressed in different timezones

- **WHEN** a scraped concert has `start_at = 2026-06-01T18:00:00+09:00` (JST)
- **AND** an existing concert has `start_at = 2026-06-01T09:00:00Z` (UTC)
- **AND** both have the same `local_event_date` and `listed_venue_name`
- **THEN** the scraped concert SHALL be treated as a duplicate
- **AND** SHALL NOT be published in the `concert.discovered.v1` event

#### Scenario: Scraped concert has nil start_at, existing has start_at

- **WHEN** a scraped concert has `start_at = nil`
- **AND** an existing concert has a non-nil `start_at`
- **AND** both have the same `local_event_date` and `listed_venue_name`
- **THEN** the scraped concert SHALL be treated as a duplicate
- **AND** SHALL NOT be published
- **AND** the nil `start_at` SHALL NOT overwrite the existing value (the existing record already has richer information)

#### Scenario: Scraped concert has start_at, existing has nil

- **WHEN** a scraped concert has a non-nil `start_at`
- **AND** an existing concert has `start_at = nil`
- **AND** both have the same `local_event_date` and `listed_venue_name`
- **THEN** the scraped concert SHALL be published in the `concert.discovered.v1` event
- **AND** the downstream UPSERT SHALL update the existing record's `start_at` with the newly discovered value

#### Scenario: Both have non-nil start_at representing different instants

- **WHEN** a scraped concert has a non-nil `start_at`
- **AND** an existing concert has a non-nil `start_at`
- **AND** both have the same `local_event_date` and `listed_venue_name`
- **AND** the two `start_at` values represent different instants after UTC normalization (e.g., matinee 13:00 UTC vs evening 18:00 UTC)
- **THEN** the scraped concert SHALL be treated as a distinct event (separate show)
- **AND** SHALL be published in the `concert.discovered.v1` event

#### Scenario: Both have nil start_at, same date and venue

- **WHEN** a scraped concert has `start_at = nil`
- **AND** an existing concert has `start_at = nil`
- **AND** both have the same `local_event_date` and `listed_venue_name`
- **THEN** the scraped concert SHALL be treated as a duplicate
- **AND** SHALL NOT be published

#### Scenario: Same date, different venue

- **WHEN** a scraped concert has the same `local_event_date` as an existing concert
- **AND** the `listed_venue_name` values differ
- **THEN** the scraped concert SHALL be treated as a distinct event
- **AND** SHALL be published regardless of `start_at` values

#### Scenario: Different date, same venue

- **WHEN** a scraped concert has a different `local_event_date` from an existing concert
- **AND** the `listed_venue_name` values match
- **THEN** the scraped concert SHALL be treated as a distinct event
- **AND** SHALL be published regardless of `start_at` values

#### Scenario: Within-batch dedup — same instant in different timezones

- **WHEN** two scraped concerts in the same Gemini response have the same `local_event_date` and `listed_venue_name`
- **AND** their `start_at` values represent the same instant after UTC normalization
- **THEN** only the first concert SHALL be included in the `concert.discovered.v1` event
- **AND** the second SHALL be discarded as a within-batch duplicate

#### Scenario: Within-batch — genuinely different start_at at same venue

- **WHEN** two scraped concerts in the same Gemini response have the same `local_event_date` and `listed_venue_name`
- **AND** their `start_at` values represent different instants after UTC normalization
- **THEN** both concerts SHALL be included in the `concert.discovered.v1` event (matinee/evening shows)

### Requirement: Dedup Key Comparison for Existing Concerts

The dedup logic SHALL build a lookup set from existing DB concerts using `ListByArtist(upcomingOnly=true)`. The `listed_venue_name` for existing concerts SHALL be read from `Event.ListedVenueName`. When `Event.ListedVenueName` is `nil` (legacy rows inserted before this field was added), the existing concert SHALL be excluded from the dedup set (it cannot match any scraped concert by venue name).

#### Scenario: Existing concert with nil ListedVenueName is skipped

- **WHEN** an existing concert has `ListedVenueName = nil` (legacy data)
- **THEN** it SHALL NOT be added to the dedup lookup set
- **AND** scraped concerts SHALL NOT be matched against it

#### Scenario: Existing concert with non-nil ListedVenueName is included

- **WHEN** an existing concert has a non-nil `ListedVenueName`
- **THEN** it SHALL be added to the dedup lookup set using `(local_event_date, listed_venue_name, start_at_utc)` as the key

### Requirement: Resilience to Gemini API Non-Determinism

The Gemini API does not guarantee deterministic responses across calls. The dedup logic SHALL be resilient to the following known variations without creating duplicate records.

#### Scenario: Title variation across runs

- **WHEN** Gemini returns a concert with the same `local_event_date`, `listed_venue_name`, and `start_at` as an existing concert
- **AND** the `title` differs slightly (e.g., trailing whitespace, different casing, added subtitle)
- **THEN** the concert SHALL still be treated as a duplicate
- **AND** SHALL NOT be published (title is not part of the dedup key)

#### Scenario: open_at variation across runs

- **WHEN** Gemini returns a concert with the same natural key as an existing concert
- **AND** the `open_at` value differs
- **THEN** the concert SHALL still be treated as a duplicate based on the natural key

#### Scenario: source_url variation across runs

- **WHEN** Gemini returns a concert with the same natural key as an existing concert
- **AND** the `source_url` differs
- **THEN** the concert SHALL still be treated as a duplicate based on the natural key

#### Scenario: admin_area variation across runs

- **WHEN** Gemini returns a concert with the same natural key as an existing concert
- **AND** the `admin_area` value differs or is newly provided
- **THEN** the concert SHALL still be treated as a duplicate based on the natural key

#### Scenario: start_at becomes nil in a later run

- **WHEN** Gemini previously returned `start_at = 18:00` for a concert
- **AND** in a subsequent run Gemini returns `start_at = nil` for the same `local_event_date` and `listed_venue_name`
- **THEN** the concert SHALL be treated as a duplicate (nil scraped start_at matches any existing start_at at the same date+venue)
- **AND** the existing `start_at` value SHALL be preserved

#### Scenario: start_at appears in a later run

- **WHEN** an existing concert has `start_at = nil`
- **AND** in a subsequent run Gemini returns `start_at = 18:00` for the same `local_event_date` and `listed_venue_name`
- **THEN** the concert SHALL be published for UPSERT to fill in the previously unknown `start_at`
