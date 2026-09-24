# Coordinates

## Purpose

Coordinates is a point on Earth given as a WGS 84 latitude and longitude, always carried together as a pair. It locates a Venue and the centroid of a Home area, and has no identity of its own.

| attribute | meaning | constraint |
|-----------|---------|------------|
| latitude | degrees north | required; any value accepted, 0 included |
| longitude | degrees east | required; any value accepted, 0 included |

## Requirements

### Requirement: Coordinates are a complete pair

Coordinates SHALL be present only as a complete latitude and longitude pair. A location with only one of the two known SHALL have no Coordinates. Any numeric value, including 0, SHALL be accepted.

#### Scenario: Zero is a valid coordinate
- **WHEN** latitude is 0.0 and longitude is 0.0
- **THEN** the Coordinates are valid

#### Scenario: Half a pair is no coordinates
- **WHEN** a latitude is known but no longitude
- **THEN** the location has no Coordinates

### Requirement: Coordinates are not shown to fans

A Venue's Coordinates SHALL be used only to classify proximity; a Venue as shown to fans SHALL carry its name and admin area but not its Coordinates.

#### Scenario: Fan concert list
- **WHEN** a fan-facing list returns a Concert whose Venue has Coordinates
- **THEN** the Venue shown carries no Coordinates
