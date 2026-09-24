<!-- spec: venue-name-cache | target: components/usecase/concert/create-from-discovered | flags: CLASSNAME | new_name: Venue lookup by listed name before Places API call -->

### Requirement: Venue lookup by listed name before Places API call

The `VenueRepository` SHALL provide a `GetByListedName` method that looks up a venue by the exact `listed_venue_name` and optional `admin_area` as stored in the `venues` table. The `ConcertCreationUseCase` SHALL call this method before invoking the Google Places API during venue resolution.

#### Scenario: Venue found by listed name — API call skipped

- **WHEN** venue resolution is performed with a `listed_venue_name` and optional `admin_area`
- **AND** a venue with the same `listed_venue_name` and `admin_area` already exists in the database
- **THEN** the system SHALL return that existing venue immediately
- **AND** the system SHALL NOT call the Google Places API

#### Scenario: Venue not found by listed name — resolution continues

- **WHEN** venue resolution is performed with a `listed_venue_name` and optional `admin_area`
- **AND** no venue with that combination exists in the database
- **THEN** the system SHALL proceed to call the Google Places API as before

#### Scenario: Listed name match is case-sensitive and exact

- **WHEN** `GetByListedName` is called
- **THEN** the lookup SHALL use exact string equality on `listed_venue_name`
- **AND** variations in casing or whitespace SHALL result in a miss (falling through to the API)
