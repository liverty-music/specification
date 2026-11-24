## Purpose

AreaUseCase.ListByCountry gives the first-level Areas, regions and time zones of one country to whoever confirms a venue's area or time zone: a member placing an event in the organizer console, or an admin approving a discovered concert.

## ADDED Requirements

### Requirement: The country's Areas, regions and time zones

ListByCountry SHALL take a country code and return the result of Area.ListByCountry for it unchanged, failures included. It SHALL store nothing.

#### Scenario: Japan's areas

- **WHEN** ListByCountry is called with `JP`
- **THEN** the 47 prefectures, the eight regions and the time zone `Asia/Tokyo` returned by Area.ListByCountry are returned

#### Scenario: Malformed country code

- **WHEN** Area.ListByCountry fails with InvalidArgument
- **THEN** ListByCountry fails with InvalidArgument
