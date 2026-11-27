# components/entity/area/list-countries Specification

## Purpose
ListCountries returns the countries and territories that have first-level Areas, with their names, so a member can pick a venue's country from a list before picking its area.

## Requirements

### Requirement: The countries that have first-level Areas

ListCountries SHALL return, once each and in code order, every country or territory that has at least one first-level Area, each with its ISO 3166-1 alpha-2 code, its English name and its Japanese name when one is published. A country with no first-level Area SHALL NOT be returned. It SHALL take no input and store nothing.

#### Scenario: Japan and Korea

- **WHEN** ListCountries is called
- **THEN** `JP` is returned with the names Japan and 日本, and `KR` with the names South Korea and 韓国

#### Scenario: Territory that is its own Area

- **WHEN** ListCountries is called
- **THEN** `HK` is returned once, with the names Hong Kong SAR China and 中華人民共和国香港特別行政区

#### Scenario: Country without first-level Areas

- **WHEN** a country code has no first-level Area
- **THEN** ListCountries does not return it
