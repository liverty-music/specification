# components/entity/venue/set-coordinates Specification

## Purpose
Stores a Venue's coordinates freshly read from the map catalog together with their fetch time, or removes them when the place no longer exists.

## Requirements

### Requirement: Replace or remove a venue's coordinates

SetCoordinates SHALL take a Venue id and either coordinates with their fetch time or no coordinates. Given coordinates, it SHALL replace the Venue's coordinates and fetch time with them; given none, it SHALL remove both. It SHALL leave the Venue's other attributes, the place id included, unchanged, and SHALL fail with NotFound when no Venue has the id.

#### Scenario: Refreshed coordinates
- **WHEN** a Venue's coordinates were fetched at 2026-11-01 04:00 UTC and SetCoordinates is given new coordinates fetched at 2026-11-24 04:00 UTC
- **THEN** the Venue holds the new coordinates with the fetch time 2026-11-24 04:00 UTC

#### Scenario: Coordinates removed
- **WHEN** SetCoordinates is given no coordinates for a Venue with coordinates and place id P
- **THEN** the Venue has no coordinates and no fetch time and keeps place id P

#### Scenario: Unknown venue
- **WHEN** no Venue has the given id
- **THEN** SetCoordinates fails with NotFound
