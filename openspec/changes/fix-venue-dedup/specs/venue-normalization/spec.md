## MODIFIED Requirements

### Requirement: Venue Enrichment Pipeline

The system SHALL provide an async enrichment pipeline that resolves raw venue names to canonical external identifiers (MusicBrainz MBID or Google Maps place_id) and updates venue records with canonical names and geographic coordinates. This pipeline now serves as a **fallback** for venues that were not resolved at creation time via the synchronous Google Places lookup.

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

#### Scenario: Venue already enriched at creation time is skipped

- **WHEN** the enrichment job runs
- **AND** a venue was resolved via Google Places API at creation time (has `google_place_id` set and `enrichment_status = 'enriched'`)
- **THEN** the venue SHALL be skipped by the enrichment pipeline

### Requirement: Venue Deduplication During Discovery

The concert discovery phase SHALL resolve venues using the Google Places API at creation time, falling back to `raw_name` lookup when the API is unavailable or returns no results.

#### Scenario: Venue resolved via Google Places API at creation time

- **WHEN** the concert creation step attempts to resolve a venue for a scraped concert
- **THEN** the system SHALL first call the Google Places API Text Search with the `listed_venue_name` and `admin_area`
- **AND** if a result is found, the system SHALL look up the venue by `google_place_id`
- **AND** if a venue record with that `google_place_id` exists, the existing venue SHALL be used
- **AND** if no venue record with that `google_place_id` exists, a new venue SHALL be created with the canonical name, `google_place_id`, coordinates, and `enrichment_status = 'enriched'`

#### Scenario: Google Places API returns no result

- **WHEN** the Google Places API Text Search returns no results for a venue name
- **THEN** the system SHALL fall back to the existing `GetByName` lookup
- **AND** if no venue is found by name, a new venue SHALL be created with `enrichment_status = 'pending'`

#### Scenario: Google Places API is unavailable

- **WHEN** the Google Places API returns a transient error (timeout, 5xx, rate limit)
- **THEN** the system SHALL fall back to the existing `GetByName` lookup
- **AND** SHALL NOT fail the entire concert creation batch

#### Scenario: Batch-local cache uses place_id as key

- **WHEN** multiple concerts in the same batch refer to the same physical venue with different text variants
- **AND** Google Places API resolves them to the same `place_id`
- **THEN** only one venue record SHALL be created
- **AND** subsequent concerts in the batch SHALL reuse the cached venue ID

#### Scenario: Enriched venue found by raw_name

- **WHEN** the concert discovery step attempts to find a venue by its scraped name
- **AND** Google Places API is not used or returns no result
- **AND** no venue record matches on `venues.name`
- **AND** a venue record matches on `venues.raw_name`
- **THEN** the existing venue record SHALL be used (no new record created)
