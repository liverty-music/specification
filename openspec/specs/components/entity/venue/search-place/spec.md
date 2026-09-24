# Venue.SearchPlace

## Purpose

Looks up a venue name, optionally with its admin area, in an external map catalog and returns the best matching place: its place id, canonical name and location.

## Requirements

### Requirement: Best match or NotFound

SearchPlace SHALL return the single best matching place for the name and admin area, and SHALL fail with NotFound when the catalog has no match and with Unavailable when the catalog cannot be reached.

#### Scenario: Known venue
- **WHEN** "日本武道館" with JP-13 is searched
- **THEN** one place with its place id and canonical name is returned

#### Scenario: No match
- **WHEN** the catalog has no match
- **THEN** SearchPlace fails with NotFound

### Requirement: Canonical name in the venue country's language

SearchPlace SHALL return the canonical name in the language of the admin area's country — Japanese for JP, Korean for KR, simplified Chinese for CN, traditional Chinese for TW — and in English for any other country or when no admin area is given.

#### Scenario: Japanese venue
- **WHEN** a venue with admin area JP-27 is searched
- **THEN** the canonical name is returned in Japanese when the catalog has one

#### Scenario: No admin area
- **WHEN** a venue is searched with no admin area
- **THEN** the canonical name is returned in English

### Requirement: Location only when known

A returned place SHALL carry Coordinates only when the catalog gives its location; otherwise it SHALL have none.

#### Scenario: Place without location
- **WHEN** the catalog's match has no location
- **THEN** the returned place has no Coordinates
