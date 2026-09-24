# Geo Location

## Purpose

A GeoLocation is a reference point supplied by a caller — a latitude, a longitude and the administrative area that contains them — against which Concerts are classified HOME, NEARBY or AWAY. It says nothing about whose location it is.

| attribute | meaning | constraint |
|-----------|---------|------------|
| latitude | WGS 84 degrees north | required, −90 to 90 |
| longitude | WGS 84 degrees east | required, −180 to 180 |
| admin area | subdivision containing the point, compared with a Venue's admin area | required, non-empty text |

## Requirements

### Requirement: GeoLocation validation

A GeoLocation SHALL be invalid (InvalidArgument) when its latitude is outside −90 to 90, its longitude is outside −180 to 180, or its admin area is empty. Any non-empty admin area text SHALL be accepted.

#### Scenario: Latitude out of range
- **WHEN** latitude is 91.0
- **THEN** the GeoLocation is invalid

#### Scenario: Longitude out of range
- **WHEN** longitude is −181.0
- **THEN** the GeoLocation is invalid

#### Scenario: Empty admin area
- **WHEN** the admin area is empty
- **THEN** the GeoLocation is invalid

#### Scenario: Non-ISO admin area text is accepted
- **WHEN** the admin area is "Tokyo" and latitude and longitude are in range
- **THEN** the GeoLocation is valid

### Requirement: Classified as a home area at the point

A Concert's proximity to a GeoLocation SHALL be its proximity to a home area whose level-1 code is the GeoLocation's admin area and whose centroid is the GeoLocation's point.

#### Scenario: Same admin area
- **WHEN** a Concert's venue admin area equals the GeoLocation's admin area
- **THEN** the Concert is HOME relative to the GeoLocation

#### Scenario: Within 200 km of the point
- **WHEN** a Concert's venue is in a different admin area and 120 km from the GeoLocation's point
- **THEN** the Concert is NEARBY relative to the GeoLocation
