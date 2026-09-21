# Search New Concerts

## Purpose

Searches external sources for new concerts on behalf of followed artists, deduplicating against existing and pending records, tolerating source inconsistencies and failures, and tracking each artist's search history, running both on demand and on a schedule.

## Requirements

### Requirement: Scheduled Concert Discovery Job

The system SHALL run a scheduled batch job that discovers new concerts for all followed artists by invoking the existing `SearchNewConcerts` use case for each artist, **except artists associated with an active organizer**. An artist associated with an active organizer SHALL be excluded from the discovery run — filtered out of the artist list **before** `SearchNewConcerts` is called (so the Gemini/search call is skipped entirely, not merely dropped downstream). Disassociating the artist (or deactivating the organizer) SHALL return it to the discovery run.

#### Scenario: Daily execution in production

- **WHEN** the CronJob triggers at 18:00 JST (09:00 UTC) daily
- **THEN** the job SHALL retrieve all distinct followed artists via `ListAllFollowed`
- **AND** call `SearchNewConcerts` for each artist not associated with an active organizer, sequentially

#### Scenario: Weekly execution in dev

- **WHEN** the CronJob is deployed in the dev environment
- **THEN** it SHALL run only on Fridays at 18:00 JST (09:00 UTC)

#### Scenario: Organizer-represented artist is skipped before search

- **WHEN** the discovery job builds its artist list and an artist is associated with an active organizer
- **THEN** the job SHALL NOT call `SearchNewConcerts` for that artist (the search/Gemini call is skipped)
- **AND** when that artist is later disassociated (or its organizer deactivated), the job SHALL call `SearchNewConcerts` for it again

### Requirement: Circuit Breaker on Consecutive Failures

The job SHALL stop processing further artists after 3 consecutive errors from `SearchNewConcerts`, treating this as a systemic failure indicator.

#### Scenario: 3 consecutive errors triggers stop

- **WHEN** `SearchNewConcerts` returns an error for 3 consecutive artists
- **THEN** the job SHALL log a warning indicating circuit break activation
- **AND** stop processing remaining artists
- **AND** exit with status code 0

#### Scenario: Successful search resets error counter

- **WHEN** `SearchNewConcerts` succeeds after 1 or 2 consecutive errors
- **THEN** the consecutive error counter SHALL reset to 0
- **AND** processing continues normally

#### Scenario: Individual artist failure is non-fatal

- **WHEN** `SearchNewConcerts` returns an error for a single artist (fewer than 3 consecutive)
- **THEN** the job SHALL log the error with the artist ID
- **AND** continue processing the next artist

### Requirement: Gemini Response Resilience

The concert search SHALL gracefully handle incomplete or invalid responses from the Gemini API by validating response completeness before JSON parsing, retrying transient failures, and classifying errors by severity.

#### Scenario: FinishReason is not STOP

- **WHEN** the Gemini API returns a response with a `FinishReason` other than `STOP` or empty string
- **THEN** the system SHALL treat this as a retryable transient error
- **AND** retry the API call within the existing backoff loop (up to max retries)
- **AND** if all retries are exhausted, log a WARN with the `FinishReason` value and response metadata
- **AND** return empty results (no error propagated to caller)

#### Scenario: Gemini returns invalid JSON with FinishReason STOP

- **WHEN** the Gemini API returns `FinishReason: STOP` but the response text is not valid JSON
- **THEN** the system SHALL treat this as a retryable transient error
- **AND** log a WARN with the first 1000 characters of the raw response text and total response length
- **AND** retry the API call within the existing backoff loop
- **AND** if all retries are exhausted, return empty results (no error propagated to caller)

#### Scenario: Valid JSON with unexpected structure

- **WHEN** the Gemini API returns valid JSON that does not match the expected `EventsResponse` schema
- **THEN** the system SHALL treat this as a permanent (non-retryable) ERROR
- **AND** log an ERROR with the response text

#### Scenario: Successful response after transient retry

- **WHEN** the Gemini API returns an invalid response on the first attempt but a valid response on a subsequent retry
- **THEN** the system SHALL parse the valid response normally
- **AND** return the discovered concerts

### Requirement: Re-discovery dedup consults published, pending, and suppression state

When the search pipeline filters newly discovered concerts, it SHALL exclude any concert whose natural key already exists in the published `events` table, as a `pending` row in the staging queue, or as a suppression entry. It SHALL NOT consult the `rejected_concerts_log` for this filtering. A suppressed natural key SHALL NOT be auto-published and SHALL NOT be re-staged as `pending`, so an operator's deletion of a bad auto-published concert is not undone by the next discovery run.

#### Scenario: Already published is skipped

- **WHEN** a discovered concert's natural key matches an existing published event
- **THEN** it SHALL NOT be staged

#### Scenario: Already pending is refreshed, not duplicated

- **WHEN** a discovered concert's natural key matches an existing `pending` staged row
- **THEN** the system SHALL update that staged row's payload with the latest discovered data
- **AND** SHALL NOT create a second `pending` row for the same natural key

#### Scenario: Previously rejected is not suppressed

- **WHEN** a discovered concert's natural key matches only a `rejected_concerts_log` entry (and is
  absent from `events` and `pending` staging)
- **THEN** the concert SHALL be staged as `pending`

#### Scenario: Suppressed concert is not re-created

- **WHEN** a discovered concert's natural key matches a suppression entry
- **THEN** the concert SHALL NOT be auto-published
- **AND** SHALL NOT be staged as `pending`

#### Scenario: Un-suppressed concert can be discovered again

- **WHEN** a suppression entry for a natural key has been removed through the deliberate
  un-suppress path
- **AND** a later discovery run produces that natural key
- **AND** that natural key is absent from `events` and `pending` staging
- **THEN** the concert SHALL be eligible for auto-publish or conflict staging as normal

### Requirement: Search Concerts by Artist

The system SHALL provide a way to search for future concerts of a specific artist using generative AI grounding. The system SHALL check the search log before calling the external API and skip the call when **either** a recent search exists **or** a new concert was recently discovered. The freshness window SHALL be configurable (default 24 hours) rather than fixed. The extracted concert data SHALL include the venue's administrative area (`admin_area`) when it can be determined with confidence. The `SearchNewConcerts` RPC SHALL be accessible without authentication to support guest onboarding flows. Error returns SHALL include contextual wrapping indicating which operation failed.

#### Scenario: Successful Search

- **WHEN** `SearchNewConcerts` is called for an existing artist
- **AND** no search log exists, or the last search was longer ago than the configured freshness TTL
- **AND** no new concert was discovered for the artist within the configured discovery-skip window (default 14 days)
- **THEN** the system MUST call the external search API
- **AND** return a list of upcoming concerts found on the web
- **AND** each concert includes title, listed venue name, date, and optionally start time and `admin_area`
- **AND** results exclude concerts that are already stored in the database

#### Scenario: Skip search when recently searched

- **WHEN** `SearchNewConcerts` is called for an artist
- **AND** a search log exists with `searched_at` within the configured freshness TTL
- **THEN** the system MUST NOT call the external search API
- **AND** return an empty list

#### Scenario: Configurable freshness TTL per environment

- **WHEN** the freshness TTL is configured to 72 hours (e.g. in production) via the search-cache-TTL setting
- **AND** a search log exists with `searched_at` 50 hours ago
- **THEN** the system MUST treat the search as fresh and MUST NOT call the external API
- **AND** when the TTL is left unset, the system MUST default to 24 hours

#### Scenario: Skip search when recently discovered a new concert

- **WHEN** `SearchNewConcerts` is called for an artist
- **AND** the artist's search log records a `last_found_at` within the configured discovery-skip window (default 14 days)
- **THEN** the system MUST NOT call the external search API
- **AND** return an empty list
- **AND** this skip applies even if the last search itself is older than the freshness TTL

#### Scenario: Do not skip on discovery when never discovered

- **WHEN** `SearchNewConcerts` is called for an artist
- **AND** the artist's search log has no `last_found_at` recorded (null)
- **AND** no recent-search freshness skip applies
- **THEN** the discovery-recency check MUST NOT cause a skip
- **AND** the system MUST proceed to call the external search API

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
- **AND** the search log cache SHALL prevent abuse by skipping external API calls for recently searched or recently discovered artists

#### Scenario: Successful Search with known official site

- **WHEN** `SearchNewConcerts` is called for an existing artist
- **AND** the artist has a persisted official site record
- **THEN** the system returns a list of upcoming concerts found on the web
- **AND** each concert includes title, venue, date, and start time
- **AND** results exclude concerts that are already stored in the database
- **AND** results exclude concerts that are already present in the approval queue in `pending` state

#### Scenario: Successful Search without official site

- **WHEN** `SearchNewConcerts` is called for an existing artist
- **AND** the artist has no persisted official site record
- **THEN** the system SHALL still perform the external search using the artist name
- **AND** return a list of upcoming concerts if found
- **AND** NOT return an error solely because the official site is missing

#### Scenario: No Results

- **WHEN** no upcoming concerts are found for the artist
- **THEN** the system returns an empty list without error

#### Scenario: Error context in failures

- **WHEN** any internal operation fails (get artist, list existing concerts, search external API)
- **THEN** the error SHALL be wrapped with `fmt.Errorf` indicating which step failed
- **AND** the original error SHALL be preserved via `%w` verb

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

The concert search's dedup logic SHALL use the natural key `(local_event_date, listed_venue_name, start_at_utc)` to determine whether a scraped concert already exists in the database. The comparison SHALL normalize timezone differences and handle `start_at` nil states according to the rules defined below. The dedup SHALL apply both when comparing scraped concerts against existing DB records and when comparing scraped concerts within the same batch.

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

### Requirement: Dedup Tolerates Venue Name Drift

The concert dedup natural key SHALL compare its `listed_venue_name` component (as defined by
the "Concert Deduplication Natural Key" requirement) on a normalized form rather than as a raw
string, so that the same physical venue reported
under different surface strings across discovery runs (for example
`フェスティバルホール` vs `大阪・フェスティバルホール`, or `新潟テルサ` vs
`新潟・新潟テルサ`) is recognised as the same venue and does not defeat deduplication
against existing events or pending staged rows. Normalization SHALL at minimum fold
whitespace and full/half-width variants and strip leading administrative-area or
city-prefix decorations (e.g. `〈admin_area〉・`, `〈city〉公演 ＠`). The `(local_event_date,
start_at)` components of the natural key SHALL be unchanged. The event natural key
`(venue_id, local_event_date, start_at)` SHALL remain the final database-level safety net
when normalization is insufficient.

#### Scenario: Prefixed venue name matches the same unprefixed venue

- **WHEN** a scraped concert has `listed_venue_name = "フェスティバルホール"`
- **AND** an existing event at the same `local_event_date` and `start_at` was stored with
  `listed_venue_name = "大阪・フェスティバルホール"`
- **THEN** the scraped concert SHALL be treated as a duplicate after name normalization
- **AND** SHALL NOT be published in the `concert.discovered.v1` event

#### Scenario: Normalization does not merge genuinely different venues

- **WHEN** two scraped concerts share `local_event_date` and `start_at`
- **AND** their venue names normalize to different values
- **THEN** they SHALL remain distinct events
- **AND** both SHALL be eligible for publication

#### Scenario: Drifted name recognised against a pending staged row

- **WHEN** a scraped concert normalizes to the same venue, date, and start as a concert
  already present in the approval queue in `pending` state
- **THEN** the scraped concert SHALL be treated as already-known
- **AND** SHALL NOT be re-staged

### Requirement: Track Concert Search History and Last Discovery Time

The system SHALL maintain a log of when each artist's concerts were last searched via external sources. The log is keyed by artist ID and records the timestamp of the most recent search (`searched_at`) in `latest_search_logs`. The system SHALL also record, per artist, the timestamp at which a search most recently discovered at least one genuinely new concert (`last_found_at`); this timestamp drives the discovery-recency skip in concert search and is distinct from `searched_at` (which records every search attempt, productive or not).

#### Scenario: Record search after Gemini call

- **WHEN** `SearchNewConcerts` completes a Gemini API call for an artist
- **THEN** the system MUST upsert a record in `latest_search_logs` with the artist's ID and the current timestamp

#### Scenario: First search for an artist

- **WHEN** no search log exists for the given artist
- **THEN** the system MUST insert a new record with the current timestamp

#### Scenario: Subsequent search for an artist

- **WHEN** a search log already exists for the given artist
- **THEN** the system MUST update the existing record's `searched_at` to the current timestamp

#### Scenario: Record discovery when new concerts are published

- **WHEN** a search for an artist produces one or more new concerts after deduplication (i.e. a `concert.discovered` event is published)
- **THEN** the system MUST set the artist's `last_found_at` to the current timestamp in `latest_search_logs`

#### Scenario: Do not record discovery when nothing new is found

- **WHEN** a search for an artist completes but yields no new concerts after deduplication
- **THEN** the system MUST NOT modify the artist's `last_found_at`
- **AND** the existing `last_found_at` value (if any) MUST be preserved

#### Scenario: Never discovered

- **WHEN** an artist has never had a search produce a new concert
- **THEN** the artist's `last_found_at` MUST be null

### Requirement: ConcertService handler timeout isolation

The ConcertService RPC handlers SHALL have a dedicated handler timeout of 120 seconds, separate from the default handler timeout applied to other services. This accommodates the Gemini API + Google Search grounding response time (25-110 seconds).

#### Scenario: SearchNewConcerts completes within 120 seconds

- **WHEN** `SearchNewConcerts` is called and the Gemini API responds within 120 seconds
- **THEN** the RPC SHALL return successfully with discovered concerts

#### Scenario: SearchNewConcerts exceeds 120 seconds

- **WHEN** `SearchNewConcerts` is called and the handler timeout of 120 seconds is exceeded
- **THEN** the RPC SHALL return a deadline exceeded error to the client

#### Scenario: Other services retain default timeout

- **WHEN** an RPC on UserService or ArtistService is called
- **THEN** the default handler timeout (60 seconds) SHALL apply
- **AND** the ConcertService timeout SHALL NOT affect other services

### Requirement: Step 1 fills in missing years from page context for partial dates

When the source page emits a date without a year (e.g. `01.16. sat`, `8月7日`), Step 1 SHALL infer the year from page context — the tour title's year range, the page heading, surrounding chronological references — and prefix the verbatim raw value with that year. The emitted `<local_date>` SHALL therefore always carry a 4-digit year as its first token.

#### Scenario: Tour title spans two years and the date is in the second year

- **WHEN** Step 1 reads a page titled "TOUR 2026-2027" with an entry `01.16. sat` after a header listing earlier 2026 dates
- **THEN** the emitted `<local_date>` SHALL be `2027.01.16. sat`

#### Scenario: Tour title spans two years and the date is in the first year

- **WHEN** Step 1 reads the same "TOUR 2026-2027" page with an entry `08.01. sat` near the start of the schedule
- **THEN** the emitted `<local_date>` SHALL be `2026.08.01. sat`

#### Scenario: Source already provides the year

- **WHEN** the source page emits `2026年3月15日(土)` for an event
- **THEN** Step 1 SHALL emit `<local_date>2026年3月15日(土)</local_date>` verbatim with no year prepended

### Requirement: Deduplication keys on (local_date, venue, start_time)

Discovered concerts SHALL be deduplicated by the triple `(local_date, venue, start_time)` before being returned. Two events with identical `(local_date, venue)` but different `start_time` (e.g. 1st-stage 18:00 / 2nd-stage 21:00) SHALL survive as distinct results. Events with identical triples SHALL be folded to a single result, preserving the first occurrence's metadata.

#### Scenario: 1st-stage / 2nd-stage preservation

- **WHEN** the input drafts contain two events at `(2026-08-07, ビルボードライブ大阪, 18:00)` and `(2026-08-07, ビルボードライブ大阪, 21:00)`
- **THEN** the final result SHALL contain both events as distinct entries

#### Scenario: Identical triple → fold

- **WHEN** the input drafts contain two events with identical `(local_date, venue, start_time)` triples
- **THEN** the final result SHALL contain exactly one entry for that triple

#### Scenario: Cross-slice duplicate at the 12-month boundary → fold

- **WHEN** two overlapping search windows (a near-term window and a far-term window) both extract the same event at their shared boundary date (i.e., the near window's end date equals the far window's start date, at now + 12 months), producing two drafts with identical `(local_date, venue, start_time)` triples (e.g. `(2027-05-25, 日本武道館, 18:00:00+09:00)`)
- **THEN** the deduplication SHALL return exactly one discovered concert for that triple
- **AND** SHALL NOT distinguish which of the two search windows the result came from in the merged output

### Requirement: Discovered concert fields preserve the source page's original language

Step 1 SHALL copy every extracted field — venue in particular — verbatim in the language it is written on the source page, and SHALL NOT translate, romanize, anglicize, or otherwise localize any value, even when the page offers an English or otherwise multilingual view. A Japanese venue name SHALL be emitted in Japanese.

#### Scenario: Multilingual tour page — Japanese venue retained

- **WHEN** Step 1 extracts an event whose venue is printed as `幕張メッセ 9・11ホール` on a page that also offers an English view rendering it "Makuhari Messe Halls 9 & 11"
- **THEN** the emitted `<venue>` SHALL be `幕張メッセ 9・11ホール`
- **AND** it SHALL NOT be romanized or translated to English

#### Scenario: Renamed venue kept verbatim, not semantically translated

- **WHEN** the source prints a venue such as `クロコくんホール（旧 日本ガイシホール）`
- **THEN** the emitted `<venue>` SHALL reproduce that Japanese string verbatim
- **AND** it SHALL NOT be rendered as an English gloss such as "Crocodile Hall"

### Requirement: Discovered concert source URL prefers the tour-specific page

For each extracted tour or show, Step 1 SHALL set `source_url` to the artist's page dedicated to THAT specific tour/show — a tour special/feature page or the specific announcement article — in preference to the official-site top page or a generic news-list page, choosing the most detailed tour-specific candidate.

#### Scenario: Tour feature page preferred over the site top

- **WHEN** a tour has a dedicated feature page (e.g. a `/feature/<tour>` page) and the artist also has an official-site top page
- **THEN** `source_url` SHALL be the tour feature page, not the site top page

#### Scenario: No tour-specific page available

- **WHEN** no tour-specific page exists and only a general news-list or top page is available
- **THEN** Step 1 MAY use the most detailed available official page as `source_url`

### Requirement: Search and track new concerts for followed artists

The `ConcertServiceClient` singleton SHALL provide a `searchAndTrack(artistId, signal, targetCount, onConcertFound?)` method that encapsulates the full search lifecycle: initiate backend search, poll for completion, verify concerts on completion, and accumulate results in `artistsWithConcerts`. The service SHALL own an observable set of artist IDs (`artistsWithConcerts`) tracking which artists have confirmed concerts.

#### Scenario: searchAndTrack initiates backend search

- **WHEN** `searchAndTrack(artistId)` is called
- **AND** the artist is not already tracked
- **THEN** the system SHALL call `searchNewConcerts(artistId)` fire-and-forget
- **AND** the system SHALL start polling via `setInterval` (2000ms) if not already running

#### Scenario: searchAndTrack for already-tracked artist is no-op

- **WHEN** `searchAndTrack(artistId)` is called for an artist already in the tracking map
- **THEN** the system SHALL NOT initiate a new search or duplicate the tracking entry

#### Scenario: Poll detects search completion

- **WHEN** `listSearchStatuses` returns `completed` for an artist
- **THEN** the system SHALL call `listConcerts(artistId)`
- **AND** if concerts exist, the system SHALL add `artistId` to `artistsWithConcerts`
- **AND** if an `onConcertFound` callback was provided, the system SHALL invoke it with the artist ID

#### Scenario: Poll detects search failure

- **WHEN** `listSearchStatuses` returns `failed` for an artist
- **THEN** the system SHALL mark the artist as done without checking concerts

#### Scenario: Per-artist timeout

- **WHEN** an artist's search has been pending for >= 15 seconds
- **THEN** the system SHALL mark the artist as done (timeout)

#### Scenario: Early polling stop at target

- **WHEN** `artistsWithConcerts.size` reaches the provided target count
- **THEN** the system SHALL stop polling immediately via `clearInterval`

#### Scenario: All searches complete stops polling

- **WHEN** all tracked artists have status `done`
- **AND** `artistsWithConcerts.size` has not yet reached the target
- **THEN** the system SHALL stop polling

#### Scenario: AbortSignal cancels polling

- **WHEN** the provided `AbortSignal` is aborted (e.g., page navigation)
- **THEN** the system SHALL stop polling via `clearInterval`
- **AND** the system SHALL retain `artistsWithConcerts` state (not clear it)

#### Scenario: artistsWithConcertsCount getter

- **WHEN** `artistsWithConcertsCount` is accessed
- **THEN** it SHALL return `artistsWithConcerts.size`
