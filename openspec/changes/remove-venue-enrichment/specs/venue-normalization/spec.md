## ADDED Requirements

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

## REMOVED Requirements

### Requirement: Venue Enrichment Pipeline

**Reason**: Venue resolution is now synchronous via Google Places API at concert creation time. The async enrichment pipeline (MusicBrainz → Google Maps fallback) is redundant and produces unusable data when both sources fail.

**Migration**: Venues are resolved at creation time. Unresolvable venues cause concerts to be skipped with structured logging for manual review.

### Requirement: Google Maps Authentication via Workload Identity

**Reason**: The Google Maps venue searcher used by the enrichment pipeline is removed. Google Places API authentication for concert creation is handled by the existing Gemini-based searcher infrastructure.

**Migration**: No action required. The Gemini searcher's authentication remains unchanged.

### Requirement: Enrichment Error Logging Consolidation

**Reason**: The enrichment pipeline that generated these logs is removed.

**Migration**: Replaced by skip-concert Warn logs in the concert creation pipeline.

### Requirement: Venue Duplicate Merge

**Reason**: Venue deduplication is now handled at creation time via `google_place_id` lookup (`GetByPlaceID`). The post-hoc merge during enrichment is no longer needed.

**Migration**: `GetByPlaceID` in the concert creation flow prevents duplicates from being created in the first place.

### Requirement: Venue Enrichment Status Tracking

**Reason**: All venues are now created in an enriched state (with Google Places canonical name and coordinates) or not created at all. The `enrichment_status` lifecycle is eliminated.

**Migration**: The `enrichment_status` column, `venue_enrichment_status` enum, `raw_name` column, and `mbid` column are dropped from the `venues` table.

### Requirement: Enrichment Job Execution

**Reason**: The enrichment job is removed along with the enrichment pipeline.

**Migration**: No action required. The concert-discovery CronJob no longer has a venue enrichment post-step.

### Requirement: Venue Deduplication During Discovery

**Reason**: `raw_name`-based fallback lookup is removed. Venue deduplication is now based on `google_place_id` via `GetByPlaceID`, which is more reliable than name matching.

**Migration**: Venue lookup uses `GetByPlaceID` instead of `GetByName`/`raw_name` fallback.

## MODIFIED Requirements

### Requirement: Venue Resolution During Concert Creation

The concert creation pipeline SHALL resolve venues synchronously via Google Places API. The `placeSearcher` dependency is required (not optional). Name-based fallback (`GetByName`) is removed.

#### Scenario: Successful venue resolution via Places API

- **WHEN** the concert creation pipeline processes a scraped concert
- **AND** Google Places API returns a match
- **THEN** the system SHALL look up an existing venue by `google_place_id` via `GetByPlaceID`
- **AND** if no existing venue is found, the system SHALL create a new venue with canonical name, coordinates, and `google_place_id` from the Places API result

#### Scenario: Venue already exists by place_id

- **WHEN** the concert creation pipeline processes a scraped concert
- **AND** Google Places API returns a match
- **AND** a venue with the same `google_place_id` already exists in the database
- **THEN** the existing venue SHALL be reused (no new venue created)

#### Scenario: Venue found in batch-local cache

- **WHEN** the concert creation pipeline processes a scraped concert
- **AND** the venue's `google_place_id` matches a venue already resolved in the current batch
- **THEN** the cached venue SHALL be reused without additional database or API calls
