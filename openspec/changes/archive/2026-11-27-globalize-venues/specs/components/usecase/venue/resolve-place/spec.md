## Purpose

VenueUseCase.ResolvePlace lets a member of an Organizer who picked a place for an event see what it will be: the stored Venue when one holds the place, otherwise a place draft (the place's name, country, suggested admin area and time zone) for the member to edit or confirm before saving.

## ADDED Requirements

### Requirement: The stored Venue, or a place draft to confirm

ResolvePlace SHALL take the caller's Organizer and a place id and fail with InvalidArgument when the place id is empty. When a Venue holds the place id (Venue.GetByPlaceID), ResolvePlace SHALL return that Venue with its name, admin area and time zone, and SHALL NOT read the map catalog. Otherwise it SHALL read the place (Venue.GetPlace) and the first-level Areas and time zones of the place's country (Area.ListByCountry), and return a place draft carrying:

- the place's name;
- the place's country;
- the place's suggested admin area, absent when the place has none;
- a time zone: the suggested Area's time zone when that Area has one; otherwise the place's time zone when it is one of the country's time zones; otherwise none.

ResolvePlace SHALL store nothing. A NotFound or Unavailable failure of Venue.GetPlace SHALL be returned unchanged.

#### Scenario: Place already a Venue
- **WHEN** a member resolves a place id that a Venue in JP-13 with time zone Asia/Tokyo holds
- **THEN** that Venue is returned with its name, JP-13 and Asia/Tokyo, and the map catalog is not read

#### Scenario: New place in an area with one time zone
- **WHEN** a member resolves the place id of Gocheok Sky Dome, which no Venue holds and whose suggested admin area is KR-11
- **THEN** a place draft with the name Gocheok Sky Dome, the country KR, the suggested admin area KR-11 and the time zone Asia/Seoul is returned, and no Venue is stored

#### Scenario: Area without a single time zone
- **WHEN** the place's suggested admin area is US-TX, which has no time zone of its own, and the map catalog gives the place the time zone America/Chicago
- **THEN** the place draft carries the time zone America/Chicago

#### Scenario: Catalog time zone of another country
- **WHEN** the place lies in the country US, its suggested admin area has no time zone of its own, and the map catalog gives the time zone Asia/Tokyo
- **THEN** the place draft carries no time zone

#### Scenario: Place without a suggested area
- **WHEN** the place read from the map catalog has no suggested admin area
- **THEN** the place draft carries no suggested admin area

#### Scenario: Empty place id
- **WHEN** a member resolves an empty place id
- **THEN** ResolvePlace fails with InvalidArgument and neither the Venues nor the map catalog are read

#### Scenario: Unknown place id
- **WHEN** Venue.GetPlace fails with NotFound
- **THEN** ResolvePlace fails with NotFound

#### Scenario: Catalog down
- **WHEN** Venue.GetPlace fails with Unavailable
- **THEN** ResolvePlace fails with Unavailable
