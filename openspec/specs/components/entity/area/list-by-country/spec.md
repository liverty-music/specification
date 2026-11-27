# components/entity/area/list-by-country Specification

## Purpose
ListByCountry returns the first-level Areas, the regions and the time zones of one country, so a member or an admin can pick the area and the time zone of a venue from lists instead of typing them.

## Requirements

### Requirement: The country's first-level Areas, regions and time zones

ListByCountry SHALL take a country code and return three lists: every first-level Area of that country in code order, each with its code, kind, English name, Japanese name when it has one, time zone when it has one and the codes of the regions it belongs to; every region of that country in code order, with its code, English name and Japanese name when it has one; and every time zone of that country in name order, with its name, English name and Japanese name when it has one. A lower-level or withdrawn Area SHALL NOT be returned. A country code that no Area and no time zone has SHALL return three empty lists. ListByCountry SHALL fail with InvalidArgument when the country code is not exactly two uppercase letters.

#### Scenario: Japan

- **WHEN** ListByCountry is called with `JP`
- **THEN** it returns the 47 prefectures `JP-01` to `JP-47` in that order, each with the time zone `Asia/Tokyo`, `JP-13` listing `JP-KANTO` among its regions; the eight regions, `JP-KANTO` among them; and the one time zone `Asia/Tokyo`

#### Scenario: Country with several time zones

- **WHEN** ListByCountry is called with `US`
- **THEN** `US-CA` is returned with the time zone `America/Los_Angeles`, `US-TX` without a time zone, and both `America/Los_Angeles` and `America/Chicago` are among the time zones

#### Scenario: Lower levels left out

- **WHEN** ListByCountry is called with `FR`
- **THEN** `FR-NAQ` is among the returned Areas and neither `FR-33` nor `FR-75` is

#### Scenario: Territory without subdivisions

- **WHEN** ListByCountry is called with `HK`
- **THEN** it returns the one Area `HK` of kind country, no region, and the one time zone `Asia/Hong_Kong`

#### Scenario: Country without Areas

- **WHEN** ListByCountry is called with a country code that no Area and no time zone has
- **THEN** it returns three empty lists

#### Scenario: Malformed country code

- **WHEN** ListByCountry is called with `jp` or `JPN`
- **THEN** it fails with InvalidArgument
