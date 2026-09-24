# Venue.Get

## Purpose

Returns one Venue by id, with its coordinates when known.

## Requirements

### Requirement: Get by id

Get SHALL return the Venue with the given id, with its name, admin area, place id, listed venue name and Coordinates when both latitude and longitude are known; it SHALL fail with NotFound when no Venue has that id.

#### Scenario: Unknown id
- **WHEN** no Venue has the id
- **THEN** Get fails with NotFound

#### Scenario: Venue without coordinates
- **WHEN** the Venue's location is not known
- **THEN** the returned Venue has no Coordinates
