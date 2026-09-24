# Venue.GetByPlaceID

## Purpose

Returns the Venue that holds a given map place identity.

## Requirements

### Requirement: Get by place id

GetByPlaceID SHALL return the one Venue holding the place id, with Coordinates when known, and SHALL fail with NotFound when no Venue holds it.

#### Scenario: Place id held
- **WHEN** a Venue holds place id P
- **THEN** GetByPlaceID returns it

#### Scenario: Place id unknown
- **WHEN** no Venue holds place id P
- **THEN** GetByPlaceID fails with NotFound
