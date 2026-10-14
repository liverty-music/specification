## Purpose

Reads one place from the external map catalog by its place id, so a Venue can be created from the place an operator picked: its canonical name, coordinates and admin area.

## ADDED Requirements

### Requirement: The place, or NotFound

GetPlace SHALL take a place id and return the place's canonical name in Japanese when the catalog has one, its coordinates and, when the place lies in a subdivision the catalog names, its admin area as an ISO 3166-2 code. It SHALL fail with NotFound when the catalog has no place with that id and with Unavailable when the catalog cannot be reached.

#### Scenario: Known place
- **WHEN** the place id of Zepp Haneda is read
- **THEN** the name Zepp Haneda (TOKYO), its coordinates and the admin area JP-13 are returned

#### Scenario: Unknown place id
- **WHEN** the catalog has no place with the given id
- **THEN** GetPlace fails with NotFound

#### Scenario: Catalog down
- **WHEN** the catalog cannot be reached
- **THEN** GetPlace fails with Unavailable
