# components/entity/venue/get-place Specification

## Purpose
Reads one place from the external map catalog by its place id - its name, country, coordinates, suggested admin area and time zone - so a member who picked it can confirm what a new Venue will be.

## Requirements

### Requirement: The place, or NotFound

GetPlace SHALL take a place id and return, for a place in any country:

- the place's name, in Japanese when the catalog has one;
- its country, as an ISO 3166-1 code;
- its coordinates with their fetch time, the moment GetPlace read them;
- a suggested admin area: the first-level Area that the region named by the place's address stands for within the place's country (see Area.Resolve), trying the region's full name first and its short name next; when the place's country is itself a first-level Area (a territory with no subdivisions, such as HK), that Area. The suggested admin area SHALL be absent when neither applies;
- the place's time zone as the catalog gives it, absent when the catalog gives none.

GetPlace SHALL store nothing. It SHALL fail with NotFound when the catalog has no place with that id and with Unavailable when the catalog cannot be reached.

#### Scenario: Known place
- **WHEN** the place id of Zepp Haneda is read
- **THEN** the name Zepp Haneda (TOKYO), the country JP, its coordinates with the time they were read, the suggested admin area JP-13 and the time zone Asia/Tokyo are returned

#### Scenario: Overseas place
- **WHEN** the place's address names the region California in the country US
- **THEN** the country US and the suggested admin area US-CA are returned

#### Scenario: Territory without subdivisions
- **WHEN** the place lies in the country HK
- **THEN** the country HK and the suggested admin area HK are returned

#### Scenario: Region that does not resolve
- **WHEN** the place's address names no region, or a region that matches no Area of the place's country
- **THEN** the place is returned without a suggested admin area

#### Scenario: No time zone from the catalog
- **WHEN** the catalog gives no time zone for the place
- **THEN** the place is returned without a time zone

#### Scenario: Unknown place id
- **WHEN** the catalog has no place with the given id
- **THEN** GetPlace fails with NotFound

#### Scenario: Catalog down
- **WHEN** the catalog cannot be reached
- **THEN** GetPlace fails with Unavailable
