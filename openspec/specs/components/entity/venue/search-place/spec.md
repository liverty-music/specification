# Venue.SearchPlace

## Purpose

Looks up a venue name, optionally with its admin area, in an external map catalog and returns the places it finds, most relevant first, each with its place id, canonical name, location, country and first-level Area; Venue.SelectPlace chooses among them.

## Requirements

### Requirement: Places in order of relevance

SearchPlace SHALL return the places the catalog finds for the name and admin area, most relevant first, and SHALL return no place and no error when the catalog has no match. It SHALL fail with Unavailable when the catalog cannot be reached. It SHALL NOT choose among the places; Venue.SelectPlace does.

#### Scenario: Known venue
- **WHEN** "日本武道館" with JP-13 is searched
- **THEN** the places found are returned, each with its place id and canonical name, most relevant first

#### Scenario: No match
- **WHEN** the catalog has no match
- **THEN** no place is returned and there is no error

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

### Requirement: Country and area of each place

SearchPlace SHALL return each place with the country its address names and the first-level Area its address stands for, found as Venue.GetPlace suggests an Area: the country itself when it is its own first-level Area (such as HK), otherwise the Area that the region's full name, then its short name, resolves to within the country (see Area.Resolve). The country is absent when the address names none; the Area is absent when the country is, or when neither the country nor the region stands for an Area. Neither case is an error.

#### Scenario: Country and area of each place
- **WHEN** the catalog's match has an address in California, United States
- **THEN** the returned place carries the country US and the first-level Area US-CA

#### Scenario: Territory without subdivisions
- **WHEN** the catalog's match has an address in Hong Kong
- **THEN** the returned place carries the country HK and the first-level Area HK

#### Scenario: Region that matches no Area
- **WHEN** the catalog's match has a United States address whose region stands for no Area
- **THEN** the returned place carries the country US and no Area

#### Scenario: Address without a country
- **WHEN** the catalog's match has no address
- **THEN** the returned place carries neither a country nor an Area
