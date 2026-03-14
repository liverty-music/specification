# venue-normalization Specification

## Purpose

The Venue Normalization capability resolves scraped venue names to canonical venue records via Google Places API during concert creation. Venues are either resolved to a canonical record (with name, coordinates, and `google_place_id`) or the concert is skipped with structured logging.

## Requirements

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
