## ADDED Requirements

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

## MODIFIED Requirements

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
