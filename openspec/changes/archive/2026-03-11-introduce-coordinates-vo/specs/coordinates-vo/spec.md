## ADDED Requirements

### Requirement: Coordinates Value Object

The system SHALL provide a `Coordinates` value object representing a WGS 84 geographic point (latitude/longitude pair). This type SHALL be used wherever geographic coordinates appear in the domain model, ensuring coordinates always travel as an atomic pair.

#### Scenario: Proto Coordinates message

- **WHEN** the `Coordinates` proto message is defined in `entity/v1/`
- **THEN** it SHALL contain a `double latitude` field
- **AND** a `double longitude` field
- **AND** no validation constraints (raw WGS 84 values, including 0.0, are valid)

#### Scenario: Go entity Coordinates struct

- **WHEN** the Go `entity.Coordinates` struct is defined
- **THEN** it SHALL contain `Latitude float64` and `Longitude float64` fields
- **AND** the struct SHALL be used as `*Coordinates` (pointer) when the coordinates are optional (e.g., unenriched venues, unsupported countries)

#### Scenario: Coordinates used by Home centroid

- **WHEN** the `Home` proto message references centroid coordinates
- **THEN** it SHALL use `optional Coordinates centroid` instead of separate `optional double` fields
- **AND** the Go `entity.Home` struct SHALL use `Centroid *Coordinates`

#### Scenario: Coordinates used by Venue location

- **WHEN** the Go `entity.Venue` struct references geographic coordinates
- **THEN** it SHALL use `Coordinates *Coordinates` instead of separate `*float64` fields
- **AND** the `entity.VenuePlace` struct SHALL likewise use `Coordinates *Coordinates`

#### Scenario: Coordinates round-trip through venue repository

- **WHEN** `VenueRepository.UpdateEnriched` is called with a venue that has non-nil `Coordinates`
- **THEN** the coordinates SHALL be persisted as `latitude` and `longitude` columns
- **AND** a subsequent `VenueRepository.Get` SHALL return the venue with `Coordinates` populated with the same values
- **WHEN** `VenueRepository.UpdateEnriched` is called with a venue that has nil `Coordinates`
- **THEN** the `latitude` and `longitude` columns SHALL be set to NULL
- **AND** a subsequent `VenueRepository.Get` SHALL return the venue with nil `Coordinates`

#### Scenario: Coordinates mapping in concert listing

- **WHEN** `ConcertRepository.ListByFollower` returns concerts with associated venues
- **AND** the venue has both `latitude` and `longitude` columns populated in the database
- **THEN** the returned `Venue.Coordinates` SHALL be non-nil with the correct latitude and longitude values
- **WHEN** either or both coordinate columns are NULL in the database
- **THEN** the returned `Venue.Coordinates` SHALL be nil

#### Scenario: PlaceSearcher adapters map external coordinates to entity.Coordinates

- **WHEN** a PlaceSearcher adapter (MusicBrainz or Google Maps) receives a response with both latitude and longitude present
- **THEN** the returned `VenuePlace.Coordinates` SHALL be non-nil with the mapped values
- **WHEN** a PlaceSearcher adapter receives a response with either or both coordinates absent
- **THEN** the returned `VenuePlace.Coordinates` SHALL be nil
