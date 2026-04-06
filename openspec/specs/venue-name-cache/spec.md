# venue-name-cache Specification

## Purpose

The Venue Name Cache capability provides a DB-first lookup for venues by their scraped `listed_venue_name` and optional `admin_area` before falling through to the Google Places API. This avoids redundant external API calls when a venue has already been resolved and persisted from a prior scrape.

## Requirements

### Requirement: Venue lookup by listed name before Places API call

The `VenueRepository` SHALL provide a `GetByListedName` method that looks up a venue by the exact `listed_venue_name` and optional `admin_area` as stored in the `venues` table. The `ConcertCreationUseCase` SHALL call this method before invoking the Google Places API during venue resolution.

#### Scenario: Venue found by listed name — API call skipped

- **WHEN** `resolveVenue` is called with a `listed_venue_name` and optional `admin_area`
- **AND** a venue with the same `listed_venue_name` and `admin_area` already exists in the database
- **THEN** the system SHALL return that existing venue immediately
- **AND** the system SHALL NOT call the Google Places API

#### Scenario: Venue not found by listed name — resolution continues

- **WHEN** `resolveVenue` is called with a `listed_venue_name` and optional `admin_area`
- **AND** no venue with that combination exists in the database
- **THEN** the system SHALL proceed to call the Google Places API as before

#### Scenario: Listed name match is case-sensitive and exact

- **WHEN** `GetByListedName` is called
- **THEN** the lookup SHALL use exact string equality on `listed_venue_name`
- **AND** variations in casing or whitespace SHALL result in a miss (falling through to the API)

### Requirement: Unique index on venue listed name and admin area

The `venues` table SHALL have a unique index on `(listed_venue_name, admin_area)` to prevent duplicate venue records for the same scraped name and area combination, and to support efficient lookup.

#### Scenario: Duplicate listed name and admin area rejected

- **WHEN** a venue is inserted with the same `listed_venue_name` and `admin_area` as an existing record
- **THEN** the database SHALL reject the insert via the unique constraint
- **AND** `VenueRepository.Create` SHALL handle the conflict gracefully (return the existing venue or ignore)

#### Scenario: Same listed name with different admin area allowed

- **WHEN** two venues share the same `listed_venue_name` but have different `admin_area` values (or one is NULL)
- **THEN** both records SHALL be permitted by the unique index
