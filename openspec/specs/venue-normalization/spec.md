# venue-normalization Specification

## Purpose

The Venue Normalization service resolves raw venue names (as scraped by the concert discovery pipeline) to canonical external identifiers via MusicBrainz and Google Maps, merges duplicate venue records, and tracks enrichment state per venue.

## Requirements

### Requirement: Venue Enrichment Pipeline

The system SHALL provide an async enrichment pipeline that resolves raw venue names to canonical external identifiers (MusicBrainz MBID or Google Maps place_id) and updates venue records with canonical names and geographic coordinates.

#### Scenario: Successful enrichment via MusicBrainz

- **WHEN** the enrichment job processes a venue with `enrichment_status = 'pending'`
- **AND** MusicBrainz place search returns a match
- **THEN** the venue record SHALL be updated with the MusicBrainz MBID
- **AND** `venues.raw_name` SHALL be set to the current `venues.name` (if `raw_name` is NULL) to preserve the original scraper-provided name
- **AND** `venues.name` SHALL be overwritten with the canonical name from MusicBrainz
- **AND** `enrichment_status` SHALL be set to `'enriched'`
- **AND** the venue's `Coordinates` SHALL be set to the value returned by the PlaceSearcher (non-nil when the response includes coordinates, nil otherwise)

#### Scenario: Successful enrichment via Google Maps fallback

- **WHEN** the enrichment job processes a venue with `enrichment_status = 'pending'`
- **AND** MusicBrainz place search returns no match
- **AND** Google Maps Text Search returns a match
- **THEN** the Google Maps client SHALL authenticate via OAuth Bearer token (not API key)
- **AND** the venue record SHALL be updated with the Google Maps place_id
- **AND** `venues.raw_name` SHALL be set to the current `venues.name` (if `raw_name` is NULL) to preserve the original scraper-provided name
- **AND** `venues.name` SHALL be overwritten with the canonical name from Google Maps
- **AND** `enrichment_status` SHALL be set to `'enriched'`
- **AND** the venue's `Coordinates` SHALL be updated from the Google Maps geometry response

#### Scenario: Both sources miss

- **WHEN** the enrichment job processes a venue with `enrichment_status = 'pending'`
- **AND** MusicBrainz returns no match
- **AND** Google Maps returns no match
- **THEN** `enrichment_status` SHALL be set to `'failed'`
- **AND** `venues.name` SHALL remain unchanged
- **AND** the venue's `Coordinates` SHALL remain nil
- **AND** the venue SHALL NOT be retried in subsequent job runs

#### Scenario: Ambiguous results (multiple matches)

- **WHEN** the enrichment job processes a venue with `enrichment_status = 'pending'`
- **AND** MusicBrainz or Google Maps returns more than one candidate match
- **THEN** the venue SHALL NOT be updated with any external identifier
- **AND** `venues.name` SHALL remain unchanged
- **AND** `enrichment_status` SHALL be set to `'failed'`
- **AND** the ambiguity SHALL be logged for future manual review

#### Scenario: admin_area used as search hint

- **WHEN** the enrichment job queries MusicBrainz or Google Maps for a venue
- **AND** the venue has a non-NULL `admin_area` (ISO 3166-2 code)
- **THEN** the system SHALL convert the ISO 3166-2 code to a locale-appropriate text name before including it in the search query
- **AND** the text name SHALL be in the language most likely to yield accurate results for the target service (e.g., Japanese for MusicBrainz JP venues, English for Google Maps)

### Requirement: Google Maps Authentication via Workload Identity

The Google Maps Places API client SHALL authenticate using OAuth 2.0 tokens obtained via Application Default Credentials (ADC) instead of an API key.

#### Scenario: OAuth token obtained via ADC in GKE

- **WHEN** the consumer pod starts in a GKE cluster with Workload Identity enabled
- **THEN** the Google Maps client SHALL obtain an OAuth 2.0 access token using `google.DefaultTokenSource` with scope `https://www.googleapis.com/auth/cloud-platform`
- **AND** the client SHALL include the token in the `Authorization: Bearer <token>` header on every Places API request
- **AND** the client SHALL include the `X-Goog-User-Project` header with the GCP project ID

#### Scenario: Google Maps searcher always registered

- **WHEN** the consumer application initializes the venue enrichment pipeline
- **THEN** the Google Maps searcher SHALL always be registered as a fallback searcher
- **AND** registration SHALL NOT be conditional on the presence of an API key environment variable

### Requirement: Enrichment Error Logging Consolidation

The venue enrichment pipeline SHALL emit structured error logs exclusively at the top-level call site with sufficient diagnostic attributes for troubleshooting.

#### Scenario: Error log emitted at top level for batch enrichment

- **WHEN** `EnrichPendingVenues` processes a venue and enrichment fails
- **THEN** a single structured log entry SHALL be emitted at the `EnrichPendingVenues` level
- **AND** the log entry SHALL include attributes: `venue_id`, `raw_name`, `error`, and `outcome` (one of `failed` or `transient`)
- **AND** no duplicate error log SHALL be emitted from `enrichOne` internals or the repository layer for the same failure

#### Scenario: Error log emitted at top level for event-driven enrichment

- **WHEN** `VenueConsumer.Handle` processes a `venue.created.v1` event and `EnrichOne` returns an error
- **THEN** a structured error log SHALL be emitted at the consumer handler level
- **AND** the log entry SHALL include attributes: `venue_id`, `venue_name`, and `error`

#### Scenario: Merge log includes diagnostic attributes

- **WHEN** a duplicate venue is detected and merged during enrichment
- **THEN** the merge Info log SHALL include attributes: `canonical_id`, `duplicate_id`, `canonical_name`, and `raw_name`

### Requirement: Venue Duplicate Merge

The system SHALL detect and merge duplicate venue records that resolve to the same external canonical identifier during the enrichment pass.

#### Scenario: Duplicate detected during enrichment

- **WHEN** the enrichment job resolves a venue to an external ID (MBID or place_id)
- **AND** another venue record already has the same external ID
- **THEN** the two records SHALL be merged within a single atomic transaction
- **AND** events in the duplicate venue that share the same `(artist_id, local_event_date, start_at)` (using NULL-safe equality for `start_at`) as events already in the canonical venue SHALL be deleted to prevent duplicate event rows
- **AND** all remaining `events.venue_id` references to the duplicate SHALL be updated to point to the canonical venue
- **AND** the duplicate venue record SHALL be deleted
- **AND** `admin_area` on the canonical record SHALL be set to `COALESCE(canonical.admin_area, duplicate.admin_area)`
- **AND** `mbid` on the canonical record SHALL be set to `COALESCE(canonical.mbid, duplicate.mbid)`
- **AND** `google_place_id` on the canonical record SHALL be set to `COALESCE(canonical.google_place_id, duplicate.google_place_id)`

#### Scenario: Canonical venue selection on merge

- **WHEN** two venue records are merged
- **THEN** the record with the older `created_at` timestamp SHALL be designated as canonical

#### Scenario: No duplicate exists

- **WHEN** the enrichment job resolves a venue to an external ID
- **AND** no other venue record shares that external ID
- **THEN** only the current venue record is updated; no merge occurs

### Requirement: Venue Enrichment Status Tracking

Each venue record SHALL carry an `enrichment_status` field reflecting the current state of the normalization pipeline.

#### Scenario: New venue defaults to pending

- **WHEN** a new venue is created (e.g., during concert discovery)
- **THEN** `enrichment_status` SHALL default to `'pending'`

#### Scenario: Enriched venue not reprocessed

- **WHEN** the enrichment job runs
- **THEN** venues with `enrichment_status = 'enriched'` or `'failed'` SHALL be excluded from processing

### Requirement: Enrichment Job Execution

The venue enrichment job SHALL run as a post-step of the existing concert-discovery CronJob.

#### Scenario: Enrichment runs after concert discovery completes

- **WHEN** the concert-discovery job finishes processing all artists
- **THEN** the venue enrichment step SHALL process all venues with `enrichment_status = 'pending'`

#### Scenario: Enrichment step failure is non-fatal

- **WHEN** the venue enrichment step encounters an error for an individual venue
- **THEN** the job SHALL log the error and continue processing the remaining pending venues
- **AND** the overall job SHALL still exit with status code 0

### Requirement: Venue Deduplication During Discovery

The concert discovery phase SHALL use `raw_name` as a fallback lookup when finding existing venue records to prevent re-creating venues that have been renamed by the enrichment pipeline.

#### Scenario: Enriched venue found by raw_name

- **WHEN** the concert discovery step attempts to find a venue by its scraped name
- **AND** no venue record matches on `venues.name`
- **AND** a venue record matches on `venues.raw_name`
- **THEN** the existing venue record SHALL be used (no new record created)
