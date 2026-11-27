## REMOVED Requirements

### Requirement: GeoLocation validation

**Reason**: An admin area that is not an Area code ("Tokyo") never equals a Venue's admin area, so a reference point carrying one silently found no HOME concert; and a reference point is now built by the server from an Area, which may have no point.
**Migration**: "GeoLocation validation with an Area code" states the rule. Callers no longer build a GeoLocation: ConcertUseCase.ListByLocation takes an area and builds it from the Area.

## ADDED Requirements

### Requirement: GeoLocation validation with an Area code

A GeoLocation SHALL be invalid (InvalidArgument) when its admin area is not in the form of a first-level Area code (two uppercase letters, optionally followed by a hyphen and 1 to 3 uppercase letters or digits), when only one of latitude and longitude is present, or when its latitude is outside −90 to 90 or its longitude outside −180 to 180. A GeoLocation with an admin area and no point SHALL be valid.

#### Scenario: Latitude out of range
- **WHEN** latitude is 91.0
- **THEN** the GeoLocation is invalid

#### Scenario: Longitude out of range
- **WHEN** longitude is −181.0
- **THEN** the GeoLocation is invalid

#### Scenario: Empty admin area
- **WHEN** the admin area is empty
- **THEN** the GeoLocation is invalid

#### Scenario: Free-text admin area
- **WHEN** the admin area is "Tokyo" and latitude and longitude are in range
- **THEN** the GeoLocation is invalid

#### Scenario: Subdivision code with a point
- **WHEN** the admin area is `JP-13` and latitude and longitude are in range
- **THEN** the GeoLocation is valid

#### Scenario: Territory code without a point
- **WHEN** the admin area is `HK` and there is no latitude and no longitude
- **THEN** the GeoLocation is valid

#### Scenario: Half a point
- **WHEN** the admin area is `JP-13` and a latitude is given without a longitude
- **THEN** the GeoLocation is invalid

## MODIFIED Requirements

### Requirement: Classified as a home area at the point

A Concert's proximity to a GeoLocation SHALL be its proximity to a home area whose level-1 code is the GeoLocation's admin area and whose centroid is the GeoLocation's point, or which has no centroid when the GeoLocation has no point.

#### Scenario: Same admin area
- **WHEN** a Concert's venue admin area equals the GeoLocation's admin area
- **THEN** the Concert is HOME relative to the GeoLocation

#### Scenario: Within 200 km of the point
- **WHEN** a Concert's venue is in a different admin area and 120 km from the GeoLocation's point
- **THEN** the Concert is NEARBY relative to the GeoLocation

#### Scenario: No point
- **WHEN** the GeoLocation has no point and a Concert's venue is in a different admin area 30 km away
- **THEN** the Concert is AWAY relative to the GeoLocation
