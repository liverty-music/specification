## MODIFIED Requirements

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
