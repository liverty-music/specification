## ADDED Requirements

### Requirement: Venue Enrichment Pipeline

The system SHALL provide an async enrichment pipeline that resolves raw venue names to canonical external identifiers (MusicBrainz MBID or Google Maps place_id) and updates venue records with canonical names.

#### Scenario: Successful enrichment via MusicBrainz

- **WHEN** the enrichment job processes a venue with `enrichment_status = 'pending'`
- **AND** MusicBrainz place search returns a match
- **THEN** the venue record SHALL be updated with the MusicBrainz MBID
- **AND** `venues.name` SHALL be overwritten with the canonical name from MusicBrainz
- **AND** `enrichment_status` SHALL be set to `'enriched'`

#### Scenario: Successful enrichment via Google Maps fallback

- **WHEN** the enrichment job processes a venue with `enrichment_status = 'pending'`
- **AND** MusicBrainz place search returns no match
- **AND** Google Maps Text Search returns a match
- **THEN** the venue record SHALL be updated with the Google Maps place_id
- **AND** `venues.name` SHALL be overwritten with the canonical name from Google Maps
- **AND** `enrichment_status` SHALL be set to `'enriched'`

#### Scenario: Both sources miss

- **WHEN** the enrichment job processes a venue with `enrichment_status = 'pending'`
- **AND** MusicBrainz returns no match
- **AND** Google Maps returns no match
- **THEN** `enrichment_status` SHALL be set to `'failed'`
- **AND** `venues.name` SHALL remain unchanged
- **AND** the venue SHALL NOT be retried in subsequent job runs

#### Scenario: admin_area used as search hint

- **WHEN** the enrichment job queries MusicBrainz or Google Maps for a venue
- **AND** the venue has a non-NULL `admin_area`
- **THEN** the `admin_area` value SHALL be included in the search query to improve match accuracy

### Requirement: Venue Duplicate Merge

The system SHALL detect and merge duplicate venue records that resolve to the same external canonical identifier during the enrichment pass.

#### Scenario: Duplicate detected during enrichment

- **WHEN** the enrichment job resolves a venue to an external ID (MBID or place_id)
- **AND** another venue record already has the same external ID
- **THEN** the two records SHALL be merged within a single atomic transaction
- **AND** all `events.venue_id` references to the duplicate SHALL be updated to point to the canonical venue
- **AND** the duplicate venue record SHALL be deleted
- **AND** `admin_area` on the canonical record SHALL be set to `COALESCE(canonical.admin_area, duplicate.admin_area)`

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
