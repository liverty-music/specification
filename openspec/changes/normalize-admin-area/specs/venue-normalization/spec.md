## MODIFIED Requirements

### Requirement: Venue Enrichment Pipeline

The system SHALL provide an async enrichment pipeline that resolves raw venue names to canonical external identifiers (MusicBrainz MBID or Google Maps place_id) and updates venue records with canonical names.

#### Scenario: Successful enrichment via MusicBrainz

- **WHEN** the enrichment job processes a venue with `enrichment_status = 'pending'`
- **AND** MusicBrainz place search returns a match
- **THEN** the venue record SHALL be updated with the MusicBrainz MBID
- **AND** `venues.raw_name` SHALL be set to the current `venues.name` (if `raw_name` is NULL) to preserve the original scraper-provided name
- **AND** `venues.name` SHALL be overwritten with the canonical name from MusicBrainz
- **AND** `enrichment_status` SHALL be set to `'enriched'`

#### Scenario: Successful enrichment via Google Maps fallback

- **WHEN** the enrichment job processes a venue with `enrichment_status = 'pending'`
- **AND** MusicBrainz place search returns no match
- **AND** Google Maps Text Search returns a match
- **THEN** the venue record SHALL be updated with the Google Maps place_id
- **AND** `venues.raw_name` SHALL be set to the current `venues.name` (if `raw_name` is NULL) to preserve the original scraper-provided name
- **AND** `venues.name` SHALL be overwritten with the canonical name from Google Maps
- **AND** `enrichment_status` SHALL be set to `'enriched'`

#### Scenario: Both sources miss

- **WHEN** the enrichment job processes a venue with `enrichment_status = 'pending'`
- **AND** MusicBrainz returns no match
- **AND** Google Maps returns no match
- **THEN** `enrichment_status` SHALL be set to `'failed'`
- **AND** `venues.name` SHALL remain unchanged
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
