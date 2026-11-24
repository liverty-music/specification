## Purpose

The admin-facing Area service boundary: an admin reviewing a discovered concert in the approval queue resolves the area they entered to its first-level Area and lists the time zones of that Area's country, to choose the time zone of a venue that has none.

## ADDED Requirements

### Requirement: Only admins reach the area calls

Resolve and ListByCountry SHALL require a signed-in caller holding the admin role. A caller who is not signed in SHALL fail with Unauthenticated; a signed-in caller without the admin role SHALL fail with PermissionDenied. Both checks come before the request is validated and before any usecase runs. Resolve SHALL then call AreaUseCase.Resolve, and ListByCountry AreaUseCase.ListByCountry.

#### Scenario: Admin lists a country's time zones

- **WHEN** a signed-in admin calls ListByCountry with `US`
- **THEN** AreaUseCase.ListByCountry runs and the Areas, regions and time zones of `US` are returned

#### Scenario: Signed-in caller without the admin role

- **WHEN** a signed-in caller without the admin role calls Resolve or ListByCountry
- **THEN** the call fails with PermissionDenied and no usecase runs

#### Scenario: Not signed in

- **WHEN** a caller who is not signed in calls Resolve or ListByCountry
- **THEN** the call fails with Unauthenticated and no usecase runs

### Requirement: Resolve returns the first-level Area of an entered area

Resolve SHALL fail with InvalidArgument, before any usecase runs, when the request carries no area text or one longer than 100 characters, or a country code that is not exactly two uppercase letters. It SHALL return the first-level Area that AreaUseCase.Resolve returns, with its code, kind, country code, English name, Japanese name when it has one and time zone when it has one, and return the usecase's failures unchanged: NotFound when the text stands for no first-level Area or for more than one.

#### Scenario: Admin enters a lower-level code

- **WHEN** a signed-in admin calls Resolve with `FR-33`
- **THEN** the Area `FR-NAQ` is returned with country code `FR`

#### Scenario: Admin enters a name with a country

- **WHEN** a signed-in admin calls Resolve with `Victoria` and country code `AU`
- **THEN** the Area `AU-VIC` is returned with country code `AU`

#### Scenario: Ambiguous name

- **WHEN** a signed-in admin calls Resolve with `Victoria` and no country code
- **THEN** it fails with NotFound

#### Scenario: Empty area text

- **WHEN** a signed-in admin calls Resolve without an area text
- **THEN** it fails with InvalidArgument and no usecase runs

### Requirement: ListByCountry takes a country code and returns what a venue is confirmed from

ListByCountry SHALL fail with InvalidArgument, before any usecase runs, when the request carries no country code or one that is not exactly two uppercase letters. It SHALL return every first-level Area with its code, kind, English name, Japanese name when it has one, time zone when it has one and the codes of its regions; every region with its code, English name and Japanese name when it has one; and every time zone with its name, English name and Japanese name when it has one.

#### Scenario: Country with several zones

- **WHEN** a signed-in admin calls ListByCountry with `US`
- **THEN** `America/Los_Angeles` and `America/Chicago` are among the returned time zones, each with its names, and `US-TX` is returned without a time zone

#### Scenario: Malformed country code

- **WHEN** a signed-in admin calls ListByCountry with `usa`
- **THEN** it fails with InvalidArgument and no usecase runs
