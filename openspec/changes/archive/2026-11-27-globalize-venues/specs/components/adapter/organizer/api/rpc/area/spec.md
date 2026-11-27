## Purpose

The organizer-facing Area service boundary: a member who is placing an event lists the countries a venue can be in, then the first-level Areas, regions and time zones of the venue's country, acting for their own Organizer.

## ADDED Requirements

### Requirement: Area calls act for the caller's own active Organizer

ListCountries and ListByCountry SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's Organization. A failure of ResolveCaller SHALL be returned unchanged and no Area is read: PermissionDenied when no Organizer is linked to the Organization or the Organizer is provisioning, and FailedPrecondition when the Organizer is deactivated. ListCountries SHALL then call AreaUseCase.ListCountries, and ListByCountry AreaUseCase.ListByCountry.

#### Scenario: Areas for an active Organizer

- **WHEN** a member of an active Organizer calls ListByCountry with `JP`
- **THEN** AreaUseCase.ListByCountry runs and Japan's Areas, regions and time zone are returned

#### Scenario: Countries for an active Organizer

- **WHEN** a member of an active Organizer calls ListCountries
- **THEN** AreaUseCase.ListCountries runs and the countries are returned

#### Scenario: Areas without an Organizer

- **WHEN** no Organizer is linked to the caller's Organization and the caller calls ListByCountry or ListCountries
- **THEN** it fails with PermissionDenied and no Area is read

### Requirement: ListCountries returns each country with its names

ListCountries SHALL take no input and return every country that AreaUseCase.ListCountries returns, each with its code, its English name and its Japanese name when it has one.

#### Scenario: Country names

- **WHEN** a member of an active Organizer calls ListCountries
- **THEN** `KR` is among the returned countries, with the names South Korea and 韓国

### Requirement: ListByCountry takes a country code and returns what a venue is confirmed from

ListByCountry SHALL fail with InvalidArgument, before any usecase runs, when the request carries no country code or one that is not exactly two uppercase letters. It SHALL return every first-level Area with its code, kind, English name, Japanese name when it has one, time zone when it has one and the codes of its regions; every region with its code, English name and Japanese name when it has one; and every time zone with its name, English name and Japanese name when it has one.

#### Scenario: Prefecture with its region and zone

- **WHEN** a member of an active Organizer calls ListByCountry with `JP`
- **THEN** the Area `JP-13` is returned with its names 東京都 and Tokyo, the time zone `Asia/Tokyo` and the region code `JP-KANTO`, and the time zone `Asia/Tokyo` is returned with its names 日本 and Japan

#### Scenario: Missing country code

- **WHEN** a member calls ListByCountry without a country code
- **THEN** it fails with InvalidArgument and no usecase runs
