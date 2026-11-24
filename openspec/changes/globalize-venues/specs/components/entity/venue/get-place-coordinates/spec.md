## Purpose

Reads only the coordinates of one place from the external map catalog by its place id, so a Venue's cached coordinates can be fetched again or filled in without reading anything else about the place.

## ADDED Requirements

### Requirement: The place's coordinates, or NotFound

GetPlaceCoordinates SHALL take a place id and return the place's coordinates with their fetch time, the moment it read them, and nothing else about the place. It SHALL return no coordinates and no error when the catalog has the place but gives no location. It SHALL store nothing, SHALL fail with NotFound when the catalog has no place with that id, for example because the place no longer exists, and with Unavailable when the catalog cannot be reached.

#### Scenario: Known place
- **WHEN** the place id of Zepp Haneda is read
- **THEN** its coordinates are returned with the time they were read

#### Scenario: Place without a location
- **WHEN** the catalog has the place but gives no location for it
- **THEN** no coordinates are returned and there is no error

#### Scenario: Place no longer exists
- **WHEN** the catalog has no place with the given id
- **THEN** GetPlaceCoordinates fails with NotFound

#### Scenario: Catalog down
- **WHEN** the catalog cannot be reached
- **THEN** GetPlaceCoordinates fails with Unavailable
