# geo-location Specification

## Purpose
TBD - created by archiving change passive-concert-discovery. Update Purpose after archive.
## Requirements
### Requirement: GeoLocation Proto Entity

The system SHALL define `entity.v1.GeoLocation` in `proto/liverty_music/entity/v1/geo_location.proto` as a reusable geographic reference point for proximity-based queries. This message is semantically neutral — it is not tied to any user concept such as "home area".

#### Scenario: GeoLocation message definition

- **WHEN** the `entity.v1.GeoLocation` proto message is defined
- **THEN** it SHALL contain a `double latitude` field representing the WGS 84 latitude of the reference point
- **AND** a `double longitude` field representing the WGS 84 longitude
- **AND** a `string admin_area` field for the ISO 3166-2 subdivision code used for HOME-tier classification (e.g., `JP-13`)
- **AND** all three fields SHALL be required (non-optional)

#### Scenario: GeoLocation used as proximity reference

- **WHEN** a caller passes a `GeoLocation` to a proximity-based RPC
- **THEN** the server SHALL use `latitude` and `longitude` for Haversine distance calculation (NEARBY tier: ≤ 200 km)
- **AND** the server SHALL use `admin_area` for exact `venue.admin_area` match (HOME tier)

#### Scenario: GeoLocation is caller-agnostic

- **WHEN** `GeoLocation` is used as an RPC parameter
- **THEN** the message SHALL carry no semantic assumption about whether the coordinates represent the caller's home, current GPS location, or any other concept
- **AND** the caller is responsible for providing accurate coordinates and admin_area for the desired reference point

### Requirement: GeoLocation Field Validation

The `GeoLocation` proto message SHALL include protovalidate constraints to reject clearly invalid values before the server processes them.

#### Scenario: Latitude range enforced

- **WHEN** `ListByLocation` is called with `location.latitude < -90.0` or `location.latitude > 90.0`
- **THEN** it SHALL return an `INVALID_ARGUMENT` error via protovalidate
- **AND** the proto definition SHALL include `(buf.validate.field).double = { gte: -90.0, lte: 90.0 }` on the `latitude` field

#### Scenario: Longitude range enforced

- **WHEN** `ListByLocation` is called with `location.longitude < -180.0` or `location.longitude > 180.0`
- **THEN** it SHALL return an `INVALID_ARGUMENT` error via protovalidate
- **AND** the proto definition SHALL include `(buf.validate.field).double = { gte: -180.0, lte: 180.0 }` on the `longitude` field

#### Scenario: admin_area must be non-empty

- **WHEN** `ListByLocation` is called with `location.admin_area = ""`
- **THEN** it SHALL return an `INVALID_ARGUMENT` error via protovalidate
- **AND** the proto definition SHALL include `(buf.validate.field).string.min_len = 1` on the `admin_area` field

